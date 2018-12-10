# Generated by Django 2.0 on 2018-12-09 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0002_auto_20181209_2020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='database',
        ),
        migrations.RemoveField(
            model_name='document',
            name='database_db',
        ),
        migrations.RemoveField(
            model_name='document',
            name='database_ip',
        ),
        migrations.RemoveField(
            model_name='document',
            name='database_password',
        ),
        migrations.RemoveField(
            model_name='document',
            name='database_port',
        ),
        migrations.RemoveField(
            model_name='document',
            name='database_sid',
        ),
        migrations.RemoveField(
            model_name='document',
            name='database_username',
        ),
        migrations.RemoveField(
            model_name='document',
            name='header_line',
        ),
        migrations.RemoveField(
            model_name='document',
            name='separator',
        ),
        migrations.RemoveField(
            model_name='document',
            name='storage',
        ),
        migrations.RemoveField(
            model_name='document',
            name='table',
        ),
        migrations.AddField(
            model_name='document',
            name='db_host',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='db_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='db_password',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='db_port',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='db_sid',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='db_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='db_username',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='file_header_line',
            field=models.CharField(blank=True, max_length=3),
        ),
        migrations.AddField(
            model_name='document',
            name='file_separator',
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AddField(
            model_name='document',
            name='file_storage',
            field=models.CharField(default='Temporary - deleted after import to database', max_length=255),
        ),
        migrations.AddField(
            model_name='document',
            name='table_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]