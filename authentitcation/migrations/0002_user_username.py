# Generated by Django 2.0 on 2018-11-27 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentitcation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='example', max_length=30, verbose_name='username'),
            preserve_default=False,
        ),
    ]