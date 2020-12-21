import json
import os

from celery.result import AsyncResult
from celery_progress.backend import Progress
from core.utils import in_memory_file_to_temp
from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.generic import TemplateView
from tasks import export_task, import_task
from core.utils import DataframeUtil, AWS

from .forms import ImportFileForm
from .models import Contact, UploadContactInfo


class IndexTemplateView(TemplateView):
    template_name = "index.html"


def export_contact_view(request):
    """
    This view exorts all contacts in Excel format.
    Exporting process will be handled by celery async task.
    """
    task = export_task.delay()
    task.forget() # Necessary
    return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')


def import_contact_view(request):
    """
    The column of the excel file should be part of
    [Username, Password, Email, First Name, Last Name]
    """
    last_upload = UploadContactInfo.objects.filter(is_success=True)\
        .order_by('-pk').first()

    allow_upload = True

    if last_upload:
        # Check if last update time is greater than 3 minutes
        timedelta = timezone.now() - last_upload.upload_at
        allow_upload = (timedelta.seconds // 60) > 3

    if allow_upload:
        contact_info = UploadContactInfo.objects.create(
            document=request.FILES.get('document_file'),
            upload_at=timezone.now()
        )
        is_valid = DataframeUtil.is_valid_dataframe(contact_info.document.path)
        if is_valid:
            # Upload to AWS
            # aws_file_name = os.path.basename(contact_info.document.path)
            # aws_uploaded, aws_status = AWS.upload_file(contact_info.document.path, aws_file_name)

            aws_uploaded = True # NOTE: This line should be removed when AWS setup

            if aws_uploaded:
                task = import_task.delay(contact_info.pk)
                task.forget() # Necessary
                return HttpResponse(json.dumps({"task_id": task.id}), content_type='application/json')
            else:
                contact_info.is_success = False
                contact_info.reason = aws_status
                contact_info.save()
                return HttpResponse(status=500) # Internal Server Error
        else:
            contact_info.is_success = False
            contact_info.reason = "File is not valid."
            contact_info.save()
            return HttpResponse(status=422) # Unprocessable Entity
    else:
        return HttpResponseForbidden()

def get_progress_view(request):
    """
    Client asks each second for task progress status.
    This function returns task info using 'task_id'.
    """
    progress = Progress(request.GET.get("task_id"))
    return HttpResponse(json.dumps(progress.get_info()), content_type='application/json')


def download_file_view(request):
    """
    Returns the file that exported in 'export_contact_view' using task outfile value in the task result.
    """
    celery_result = AsyncResult(request.GET.get("task_id"))
    filepath = celery_result.result.get("data", {}).get("outfile")
    if os.path.exists(filepath):
        with open(filepath, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/ms-excel")
            outfile = os.path.basename(filepath)
            response['Content-Disposition'] = "attachment; filename=%s" % outfile
            return response
    raise Http404
