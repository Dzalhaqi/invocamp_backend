# Generated by Django 4.1.7 on 2023-04-27 15:22

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('account_app', '0006_alter_intern_img_profile_alter_recruiter_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='intern',
            name='description',
            field=tinymce.models.HTMLField(blank=True, default='Description'),
        ),
    ]
