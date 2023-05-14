from django.contrib import admin
from .models import VacancyApplication, VacancyPost
from import_export.admin import ImportExportModelAdmin
from import_export import resources


class VacancyPostResource(resources.ModelResource):
  class Meta:
    model = VacancyPost
    fields = ('id', 'title', 'provider', 'address', 'lat', 'lng',
              'salary', 'published_date', 'updated_date', 'deadline')


class VacancyApplicationResource(resources.ModelResource):
  class Meta:
    model = VacancyApplication
    fields = ('id', 'vacancy', 'applicant', 'status',
              'applied_date', 'updated_date', 'cv')


@admin.register(VacancyPost)
class VacancyPostAdmin(ImportExportModelAdmin, admin.ModelAdmin):
  model = VacancyPost

  list_display = ('title', 'id', 'provider', 'address', 'salary',
                  'published_date', 'updated_date', 'deadline')
  list_filter = ('provider', 'address', 'salary', 'published_date')
  search_fields = ('title', 'provider', 'address', 'salary', 'published_date')
  ordering = ('title', 'provider', 'address', 'salary', 'published_date')
  readonly_fields = ('published_date', 'updated_date', 'lat',
                     'lng', 'address_coordinates', 'applicants')


@admin.register(VacancyApplication)
class VacancyApplicationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
  model = VacancyApplication

  list_display = ('vacancy', 'id', 'applicant', 'status',
                  'applied_date', 'updated_date')
  list_filter = ('vacancy', 'applicant', 'status', 'applied_date')
  search_fields = ('vacancy', 'applicant', 'status', 'applied_date')
  ordering = ('vacancy', 'applicant', 'status', 'applied_date')
  readonly_fields = ('applied_date', 'updated_date', 'cv')
