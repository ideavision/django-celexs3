from django.contrib.auth.models import User
from django.db import models

class UploadContactInfo(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    document = models.FileField(upload_to='contacts')
    upload_at = models.DateTimeField(null=True, blank=True)
    is_success = models.BooleanField(default=True)
    reason = models.TextField(null=True, blank=True)


class Contact(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=80, null=True, blank=True)
    upload_info = models.ForeignKey(
        UploadContactInfo, on_delete=models.SET_NULL, null=True,
        blank=True, related_name='contacts'
    )
