# Generated by Django 2.0 on 2018-11-29 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentitcation', '0002_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='login_hash',
            field=models.CharField(default='', max_length=30, verbose_name='login_hash'),
            preserve_default=False,
        ),
    ]
