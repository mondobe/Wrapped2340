# Generated by Django 5.1.2 on 2024-10-23 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_wrapped_time_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='wrapped',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
