# Generated by Django 2.0 on 2019-01-14 13:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('fileupload', '0014_auto_20190105_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='db_strategy',
            field=models.IntegerField(choices=[(0, 'Not set'), (1, 'Rename'), (2, 'Append'), (3, 'Replace')],
                                      default=0),
        ),
        migrations.AlterField(
            model_name='document',
            name='status',
            field=models.IntegerField(
                choices=[(0, 'Created'), (1, 'Uploading'), (2, 'Succesfully uploaded'), (3, 'Paused'),
                         (-1, 'Error on uploading')], default=0),
        ),
    ]
