# Generated by Django 2.0 on 2018-12-10 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fileupload', '0003_auto_20181209_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='log',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='document',
            name='error',
            field=models.CharField(blank=True, default='', max_length=100000),
        ),
    ]
