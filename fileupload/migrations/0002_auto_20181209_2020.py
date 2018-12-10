# Generated by Django 2.0 on 2018-12-09 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fileupload', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='error',
            field=models.CharField(default='', max_length=100000),
        ),
        migrations.AddField(
            model_name='document',
            name='status',
            field=models.IntegerField(choices=[(0, 'Created'), (1, 'Uploading'), (2, 'Succesfully uploaded'), (-1, 'Error on uploading')], default=0),
        ),
        migrations.AddField(
            model_name='document',
            name='uploading_percent',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='document',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
