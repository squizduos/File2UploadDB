# Generated by Django 2.0 on 2018-12-25 09:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('fileupload', '0007_document_original_filename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='uploading_percent',
        ),
    ]
