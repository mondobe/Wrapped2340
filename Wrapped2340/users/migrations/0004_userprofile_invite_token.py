# Generated by Django 5.1.2 on 2024-10-23 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_userprofile_spotify_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='invite_token',
            field=models.CharField(default='todo01234567abcd', max_length=16),
            preserve_default=False,
        ),
    ]