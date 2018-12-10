from django.db import models

from authentitcation.models import User
# Create your models here.

DOCUMENT_STATUS = (
    (0, 'Created'),
    (1, 'Uploading'),
    (2, 'Succesfully uploaded'),
    (-1, 'Error on uploading')
)

class Document(models.Model):
    document = models.FileField(upload_to='documents/', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_storage = models.CharField(max_length=255, default="Temporary - deleted after import to database")
    file_type = models.CharField(max_length=255, default="CSV")
    file_header_line = models.CharField(max_length=3, blank=True)
    file_separator = models.CharField(max_length=14, blank=True)
    table_name = models.CharField(max_length=100, blank=True)
    db_type = models.CharField(max_length=100, blank=True)
    db_username = models.CharField(max_length=100, blank=True)
    db_password = models.CharField(max_length=100, blank=True)
    db_host = models.CharField(max_length=100, blank=True)
    db_port = models.CharField(max_length=100, blank=True)
    db_sid = models.CharField(max_length=100, blank=True)
    db_name = models.CharField(max_length=100, blank=True)
    status = models.IntegerField(choices=DOCUMENT_STATUS, default=0)
    uploading_percent = models.IntegerField(default=0)
    error = models.CharField(max_length=100000, default="", blank=True)
    log = models.TextField(default="", blank=True)