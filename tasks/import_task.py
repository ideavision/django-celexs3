import os
import shutil
import tempfile
from os import name
from re import template

from celery_progress.backend import ProgressRecorder
from contact.models import Contact, UploadContactInfo
from core.utils import DataframeUtil
from banzaitc import celery_app
from django.conf import settings
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.utils import timezone
from openpyxl import Workbook, load_workbook

from .base import BaseTask


class ImportUserFromExcelTask(BaseTask):
    """
    Imports rows of excel file into Contacts model.
    """

    name = "ImportUserFromExcelTask"

    def insert_into_row(self, row: dict) -> Contact:
        '''
        Returns Contact object.
        '''
        name = row.get('name', None) or ''
        email = row.get('email', None) or ''
        phone_number = row.get('phone number', None) or ''
        # Check if fields aren't empty.
        if phone_number.strip() != '' and email.strip() != '' and name.strip() != '':
            contact, created = Contact.objects.get_or_create(
                phone=phone_number
            )
            if created:
                contact.name = name
                contact.phone = phone_number
                contact.email = email
                contact.save()
            return contact
        return None

    def get_contact_info(self, contact_info_id):
        '''
        Returns UploadContactInfo object.

        Parameters:
        contact_info_id (int): contact info pk param.
        '''
        return UploadContactInfo.objects.get(pk=contact_info_id)

    def run(self, contact_info_id, *args, **kwargs):
        '''
        Returns task process details.
        Appends each contact row in contact table.

        Parameters:
        contact_info_id (int): contact info pk param.
        '''
        progress_recorder = ProgressRecorder(self)
        contact_info = self.get_contact_info(contact_info_id)
        try:
            dataframe = DataframeUtil.get_validated_dataframe(contact_info.document.path)
            total_record = dataframe.shape[0]
            for index, row in dataframe.iterrows():
                contact = self.insert_into_row(row)
                if contact:
                    contact_info.contacts.add(contact)
                
                # Set status of progress in backend result to notify clinet.
                progress_recorder.set_progress(
                    index + 1, total=total_record, description="Inserting row into table"
                )
                print("Inserting row %s into table" % index)

            return {
                "detail": "Successfully import user"
            }
        except Exception as e:
            contact_info.is_success = False
            contact_info.reason = str(e)
            contact_info.save()


@celery_app.task(bind=True, base=ImportUserFromExcelTask)
def import_task(self, *args, **kwargs):
    return super(type(self), self).run(*args, **kwargs)
