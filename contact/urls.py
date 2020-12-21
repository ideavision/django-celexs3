from django.urls import path

from .views import (IndexTemplateView, download_file_view, export_contact_view,
                    get_progress_view, import_contact_view)

urlpatterns = [
    path('', IndexTemplateView.as_view(), name='index'),
    path('export', export_contact_view, name='export'),
    path('import', import_contact_view, name='import'),
    path('celery-progress', get_progress_view, name='progress'),
    path('download', download_file_view, name='download'),
]
