# Generated by Django 4.1.7 on 2023-04-29 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0003_vacancypost_salary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacancyapplication',
            name='resume',
        ),
        migrations.AddField(
            model_name='vacancyapplication',
            name='cv',
            field=models.FileField(default=None, upload_to=''),
        ),
    ]
