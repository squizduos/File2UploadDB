import os
import re

from django.db import models

from authentitcation.models import User
# Create your models here.

DOCUMENT_STATUS = (
    (0, 'Created'),
    (1, 'Uploading'),
    (2, 'Succesfully uploaded'),
    (-1, 'Error on uploading')
)

ACCEPTED_EXTENSIONS = ['CSV', 'XLS', 'XLSX', 'DTA']


class Document(models.Model):
    original_filename = models.CharField(max_length=128, verbose_name="Original filename")
    document = models.FileField(upload_to='documents/', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_storage = models.CharField(
        max_length=255,
        default="Temporary - deleted after import to database",
        blank=True,
        null=True
    )
    file_type = models.CharField(max_length=255, default="CSV")
    file_header_line = models.CharField(max_length=3, blank=True)
    file_separator = models.CharField(max_length=14, blank=True)
    table_name = models.CharField(max_length=100, blank=True)
    db_connection = models.CharField(max_length=300, blank=True)
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
    percent = models.IntegerField(null=True, default=0)
    log = models.TextField(default="", blank=True)

    def get_enabled_for_editing_by_default(self):
        return [
            "file_type",
            "file_id",
            "table_name",
            "db_type",
            "db_host",
            "db_port",
            "db_username",
            "db_password",
            "db_name"
        ]

    def get_filename_witout_extension(self):
        if not self.original_filename:
            return "N/A"
        filename, extension = os.path.splitext(self.original_filename)
        return filename

    def get_file_extension(self):
        if not self.original_filename:
            return "N/A"
        filename, extension = os.path.splitext(self.original_filename)
        return extension[1:].upper()
        
    def __str__(self):
        basic_info = f"Document #{self.id} by {self.user.username}, filename {self.original_filename}"
        if not self.document.name:
            basic_info += ", deleted from server"
        if self.status == 2:
            uploaded = f"Uploaded to {self.db_host} ({self.db_type}) successfully!"
            return f"{basic_info} || {uploaded}"
        elif self.status == 1:
            uploading = f"Uploading to {self.db_host} ({self.db_type}), task_id {self.task_id}..."
            return f"{basic_info} || {uploading}"
        elif self.status == 0:
            preparing = f"Waiting for data..."
            return f"{basic_info} || {preparing}"
        else:
            failed = f"Failed to upload with error {self.error[:80]}.."
            return f"{basic_info} || {failed}"

    def save(self, *args, **kwargs):
        if self.db_host:
            self.db_connection = self.__class__.encode_db_connection(**self.__dict__)
        super(self.__class__, self).save(*args, **kwargs)
    
    DB_FIELDS = [      
        'db_type',
        'db_username',
        'db_password',
        'db_host',
        'db_port',
        'db_sid',
        'db_name'
    ]

    DB_TYPES = {
        "PostgreSQL": "postgres",
        "Oracle": "oracle+cx_oracle"
    }

    DB_TYPES_INVERSE = {
        "postgres": "PostgreSQL",
        "oracle+cx_oracle": "Oracle"
    }

    DB_TYPES_DEFAULT_DATA = {
        "PostgreSQL": {
            "db_sid": "not applicable"
        },
        "Oracle": {
            "db_name": "not applicable"
        },
        "undefined": {
            "db_sid": "not applicable",
            "db_name": "not applicable"
        }
    }

    regex = (
        "(?P<db_type>.*):\/\/(?P<db_username>.*):(?P<db_password>.*)"
        "@(?P<db_host>.*):(?P<db_port>.*)\/(?P<db_name>.*)"
    )
    regex_expression = re.compile(regex)

    @classmethod
    def encode_db_connection(cls, **kwargs) -> str:
        # if not all(key in kwargs and len(kwargs[key]) > 0 for key in cls.DB_FIELDS):
        #     return "No connection provided"
        kwargs['db_type'] = cls.DB_TYPES[kwargs['db_type']]
        if kwargs['db_type'] == cls.DB_TYPES['Oracle']:
            kwargs['db_name'] = kwargs['db_sid']
        response = (
            "{db_type}://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
        ).format(**kwargs)
        return response

    @classmethod
    def decode_db_connection(cls, db_connection: str) -> dict:
        result = {key: "" for key in cls.DB_FIELDS}
        if db_connection == 'new-pg' or db_connection == 'new-or':
            result["db_type"] = "postgres" if db_connection == "new-pg" else "oracle+cx_oracle"
        else:
            found = [m.groupdict() for m in cls.regex_expression.finditer(db_connection)]
            result.update(**found[0])
        if result['db_type'] in cls.DB_TYPES_INVERSE.keys():
            result['db_type'] = cls.DB_TYPES_INVERSE[result['db_type']]
        else:
            result['db_type'] == 'undefined'
        result.update(**cls.DB_TYPES_DEFAULT_DATA[result['db_type']])
        return result

    @classmethod
    def name_db_connection(cls, conn: str) -> dict:
        if conn == 'new-pg' or conn == 'new-or':
            return {
                "name": "New PostgreSQL" if conn == 'new-pg' else "New Oracle",
                "value": conn,
            }
        else:
            fields = cls.decode_db_connection(conn)
            to_db = fields['db_name'] if fields['db_type'] == 'PostgreSQL' else fields['db_sid']
            name = "{db_type} ({db_host}), by user {db_username}, to db {to_db}".format(**fields, to_db=to_db)
            return {
                "name": name,
                "value": conn
            }