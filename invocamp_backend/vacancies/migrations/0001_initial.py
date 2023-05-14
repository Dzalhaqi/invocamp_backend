# Generated by Django 4.1.7 on 2023-04-29 17:01

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account_app', '0007_intern_description'),
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacancyPost',
            fields=[
                ('id', models.BigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('employment_type', models.CharField(choices=[('Full Time', 'Full Time'), ('Part Time', 'Part Time'), ('Contract', 'Contract'), ('Internship', 'Internship'), ('Freelance', 'Freelance'), ('Temporary', 'Temporary'), ('Volunteer', 'Volunteer')], default='Full Time', max_length=20)),
                ('work_type', models.CharField(choices=[('Remote', 'Remote'), ('On Site', 'On Site'), ('Hybrid', 'Hybrid')], default='On Site', max_length=20)),
                ('published_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('deadline', models.DateTimeField(blank=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('lat', models.FloatField(blank=True, default=0, null=True)),
                ('lng', models.FloatField(blank=True, default=0, null=True)),
                ('address_coordinates', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('description', tinymce.models.HTMLField(blank=True)),
                ('applicants', models.ManyToManyField(blank=True, related_name='vacancy_post', to='account_app.intern')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancy_posts', related_query_name='vacancy_posts', to='account_app.recruiter')),
                ('skills', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='VacancyApplication',
            fields=[
                ('id', models.BigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('cover_letter', models.TextField(blank=True)),
                ('resume', models.FileField(upload_to='resumes/')),
                ('applied_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=255)),
                ('note', tinymce.models.HTMLField(blank=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancy_applications', related_query_name='vacancy_applications', to='account_app.intern')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancy_applications', related_query_name='vacancy_applications', to='vacancies.vacancypost')),
            ],
        ),
    ]
