# Generated by Django 5.1.2 on 2024-10-21 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_userprofile_access_token_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='spotify_id',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='token_expires',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='data_stash',
            field=models.JSONField(default=list),
        ),
    ]
