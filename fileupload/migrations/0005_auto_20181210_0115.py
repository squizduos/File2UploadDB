# Generated by Django 2.0 on 2018-12-10 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0004_auto_20181210_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(blank=True, upload_to='documents/'),
        ),
        migrations.AlterField(
            model_name='document',
            name='file_separator',
            field=models.CharField(blank=True, max_length=14),
        ),
    ]