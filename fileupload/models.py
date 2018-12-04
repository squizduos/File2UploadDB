from django.db import models

# Create your models here.

class Document(models.Model):
    document = models.FileField(upload_to='documents/')
    storage = models.CharField(max_length=255, default="Temporary - deleted after import to database")
    file_type = models.CharField(max_length=255, default="CSV")
    header_line = models.CharField(max_length=3, blank=True)
    separator = models.CharField(max_length=8, blank=True)
    table = models.CharField(max_length=100, blank=True)
    database = models.CharField(max_length=100, blank=True)
    database_username = models.CharField(max_length=100, blank=True)
    database_password = models.CharField(max_length=100, blank=True)
    database_ip = models.CharField(max_length=100, blank=True)
    database_port = models.CharField(max_length=100, blank=True)
    database_sid = models.CharField(max_length=100, blank=True)
    database_db = models.CharField(max_length=100, blank=True)
