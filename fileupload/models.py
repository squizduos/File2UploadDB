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
    original_filename = models.CharField(max_length=128, verbose_name="Original filename")
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
    task_id = models.CharField(max_length=100, blank=True)
    status = models.IntegerField(choices=DOCUMENT_STATUS, default=0)
    error = models.CharField(max_length=100000, default="", blank=True, null=True)
    log = models.TextField(default="", blank=True)

    def __str__(self):
        basic_info = f"Document #{self.id} by {self.user.username}, filename {self.original_filename}"
        if self.status == 2:
            uploaded = f"Uploading to {self.db_host} ({self.db_type}), task_id {self.task_id}..."
            return f"{basic_info} || {uploaded}"
        elif self.status == 1:
            uploading = f"Uploaded to {self.db_host} ({self.db_type}) successfully!"
            return f"{basic_info} || {uploading}"
        elif self.status == 0:
            preparing = f"Waiting for data..."
            return f"{basic_info} || {preparing}"
        else:
            failed = f"Failed to upload with error {self.error[:80]}.."
            return f"{basic_info} || {failed}"
