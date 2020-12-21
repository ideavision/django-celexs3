import os
import shutil
import tempfile
from os import name
from re import template

from celery_progress.backend import ProgressRecorder
from banzaitc import celery_app
from django.conf import settings
from contact.models import Contact
from django.http import Http404, HttpResponse
from django.utils import timezone
from openpyxl import Workbook, load_workbook
import pandas as pd

from .base import BaseTask


class ExportUserIntoExcelTask(BaseTask):
    """
    Exports contact table as excel file.
    """

    name = "ExportUserIntoExcelTask"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.queryset = Contact.objects.all()

    def get_copied_path(self):
        '''
        Returns generated unique destination path.
        '''
        destination_path = "%s/%s-exported-users.xlsx" % (tempfile.gettempdir(), int(timezone.now().timestamp()))
        return destination_path

    def create_row(self, instance: Contact):
        '''
        Returns contact fields as dict.

        Parameters:
        instance (Contact)
        '''
        return {
            'Name': instance.name,
            'Email': instance.email,
            'Phone Number': instance.phone
        }

    def create_dataframe(self):
        '''
        Returns pandas dataframe with specific clomuns.
        '''
        df = pd.DataFrame(columns=['Name', 'Email', 'Phone Number'])
        return df

    def create_workbook(self):
        '''
        Returns pandas dataframe with appended contact list.
        '''
        progress_recorder = ProgressRecorder(self)
        total_record = self.queryset.count()
        df = self.create_dataframe()
        for index, instance in enumerate(self.queryset):
            print("Appending %s into excel" % instance.name)
            df = df.append(self.create_row(instance), ignore_index=True)
            progress_recorder.set_progress(index + 1, total=total_record, description="Inserting record into row")
        return df

    def run(self, *args, **kwargs):
        '''
        Returns task process details.
        Appends each contact in excel row.
        '''
        destination_path = self.get_copied_path()
        workbook = self.create_workbook()
        # Saving Dataframe
        workbook.to_excel(destination_path, sheet_name='Contacts', index=False)  
        return {
            "detail": "Successfully export user",
            "data": {
                "outfile": destination_path
            }
        }


@celery_app.task(bind=True, base=ExportUserIntoExcelTask)
def export_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
