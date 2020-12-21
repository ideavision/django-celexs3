from django.test import TestCase
from django.core.files import File
from django.conf import settings
from django.utils import timezone
from contact.models import UploadContactInfo, Contact

import mock

class UploadContactInfoTestCase(TestCase):
    def setUp(self):
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = 'test.xlsx'
        UploadContactInfo.objects.create(
            document=file_mock,
            upload_at=timezone.now(),
            is_success=False,
            reason="Something wrong happend."
        )

    def test_file_uploaded(self):
        """UploadContactInfo that has file is correctly identified"""
        ci = UploadContactInfo.objects.first()
        # Matches that filename starts with 'test_' and ends with '.xlsx
        self.assertRegex(ci.document.name, r'test_.*\.xlsx$') 
    
    def test_process_failed(self):
        """UploadContactInfo that has been failed is correctly identified"""
        ci = UploadContactInfo.objects.first()
        self.assertEqual(ci.is_success, False)
        self.assertEqual(ci.reason, "Something wrong happend.")

class ContactTestCase(TestCase):
    def setUp(self):
        Contact.objects.create(name="John", email="john@email.com", phone="09123456789")

    def test_contact_created(self):
        """Contact is correctly identified"""
        contact = Contact.objects.first()
        self.assertEqual(contact.name, 'John')
        self.assertEqual(contact.email, 'john@email.com')
        self.assertEqual(contact.phone, '09123456789')