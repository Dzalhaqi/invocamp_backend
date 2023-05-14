from taggit.models import Tag
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin as gis_admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import CustomUser, Recruiter, Intern, WorkExperience, Education, Award, OrganizationExperience


class WorkExperienceInline(admin.StackedInline):
  model = WorkExperience


class OrganizationExperienceInline(admin.StackedInline):
  model = OrganizationExperience


class EducationInline(admin.StackedInline):
  model = Education


class AwardInline(admin.StackedInline):
  model = Award


class CustomUserResource(resources.ModelResource):
  class Meta:
    model = CustomUser
    fields = ('id', 'email', 'account_type', 'first_name',
              'last_name', 'is_active', 'is_staff', 'is_verified')


@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
  resource_class = CustomUserResource
  model = CustomUser

  list_display = ('email', 'id', 'account_type', 'first_name',
                  'last_name', 'is_active', 'is_staff', 'is_verified')
  list_filter = ('email', 'is_active',
                 'is_staff', 'account_type')
  search_fields = ('email', 'first_name', 'last_name')
  ordering = ('email',)
  fieldsets = (
      (None, {'fields': ('email', 'password')}),
      ('Personal info', {'fields': (
          'first_name', 'last_name', 'is_verified', 'account_type')}),
      ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
      ('Important dates', {'fields': ('last_login',)}),
  )
  add_fieldsets = (
      (None, {
          'classes': ('wide',),
          'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_staff', 'is_superuser'),
      }),
  )
  readonly_fields = ('date_joined',)

  # save account and make recruiter instance or intern based on account type
  def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    if obj.account_type == 'RECRUITER':
      Recruiter.objects.create(user_profile=obj)
    elif obj.account_type == 'INTERN':
      Intern.objects.create(user_profile=obj)


@admin.register(Recruiter)
class RecruiterAdmin(ImportExportModelAdmin, gis_admin.OSMGeoAdmin):
  model = Recruiter
  list_display = ('user_profile', 'company_name', 'location_name', 'location_coordinates',
                  'category_list', 'website')
  list_filter = ('category',)
  search_fields = ('company_name', 'user_profile__email')
  ordering = ('company_name',)
  readonly_fields = ('lat', 'lng')

  default_zoom = 30

  def save_model(self, request, obj, form, change):
    obj.user_id = obj.user_profile.id
    super().save_model(request, obj, form, change)

  def get_queryset(self, request):
    return super().get_queryset(request).prefetch_related('category')

  def category_list(self, obj):
    return u", ".join(o.name for o in obj.category.all())


@ admin.register(Intern)
class InternAdmin(ImportExportModelAdmin, admin.ModelAdmin):
  model = Intern
  inlines = [EducationInline, AwardInline,
             WorkExperienceInline, OrganizationExperienceInline]
  list_display = ('user_profile', 'phone_number', 'location_name',
                  'location_coordinates',)
  search_fields = ('user_profile__email', 'phone_number', 'location_name')
  ordering = ('user_profile__email',)
  readonly_fields = ('lat', 'lng')

  default_zoom = 30
