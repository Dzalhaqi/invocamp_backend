from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import models
from geopy.geocoders import Nominatim
from taggit.managers import TaggableManager
from tinymce.models import HTMLField
from traitlets import default

from .validations import validate_employee_cv, validate_location, validate_profile
import uuid


class AccountType(models.TextChoices):
  RECRUITER = 'Recruiter'
  INTERN = 'Intern'


class EducationDegree(models.TextChoices):
  HIGH_SCHOOL = 'High_school'
  DIPLOMA = 'Diploma'
  BACHELOR = 'Bachelor'
  MASTER = 'Master'
  PHD = 'PhD'


class WorkPosition(models.TextChoices):
  INTERN = 'Intern'
  JUNIOR = 'Junior'
  MIDDLE = 'Middle'
  SENIOR = 'Senior'
  LEAD = 'Lead'
  MANAGER = 'Manager'
  DIRECTOR = 'Director'
  VICE_PRESIDENT = 'Vice President'
  SENIOR_VICE_PRESIDENT = 'Senior Vice President'
  EXECUTIVE_VICE_PRESIDENT = 'Executive Vice_president'
  CHIEF_OFFICER = 'Chief Officer'
  PRESIDENT = 'President'


class OrganizationPosition(models.TextChoices):
  PRESIDENT = 'President'
  VICE_PRESIDENT = 'Vice President'
  SECRETARY = 'Secretary'
  TREASURER = 'Treasurer'
  HEAD_OF_DIVISION = 'Head of Division'
  STAFF = 'Staff'
  MEMBER = 'Member'


# class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
#   object_id = models.UUIDField(default=uuid.uuid4, editable=False)
#   content_object = GenericForeignKey('content_type', 'object_id')
#   content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

#   class Meta:
#     verbose_name = _("Tag")
#     verbose_name_plural = _("Tags")


class CustomUserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError('The Email field must be set')
    email = self.normalize_email(email)
    user = self.model(
        email=email,
        **extra_fields)
    user.set_password(password)
    user.save()
    return user

  def create_superuser(self, email, password=None, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)

    if extra_fields.get('is_staff') is not True:
      raise ValueError('Superuser must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
      raise ValueError('Superuser must have is_superuser=True.')

    return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
  email = models.EmailField(unique=True)
  email_validated = models.BooleanField(default=False)
  first_name = models.CharField(max_length=255)
  last_name = models.CharField(max_length=255, blank=True)
  account_type = models.CharField(
      max_length=10, choices=AccountType.choices, default=AccountType.INTERN)
  date_joined = models.DateTimeField(auto_now_add=True)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  is_verified = models.BooleanField(default=False)

  USERNAME_FIELD = 'email'
  EMAIL_FIELD = 'email'
  REQUIRED_FIELDS = ['first_name', 'account_type']

  objects = CustomUserManager()


class Recruiter(gis_models.Model):
  user_profile = models.OneToOneField(
      CustomUser,
      primary_key=True,
      on_delete=models.CASCADE,
      related_name='recruiters',
      related_query_name='recruiters')
  company_name = models.CharField(max_length=255, default="Company Name")
  category = TaggableManager(
      blank=True, related_name='recruiter_tags')
  website = models.URLField(blank=True)
  location_name = models.CharField(max_length=255, blank=True, validators=[
      validate_location])
  lat = models.FloatField(blank=True, null=True, default=0)
  lng = models.FloatField(blank=True, null=True, default=0)
  location_coordinates = gis_models.PointField(blank=True, null=True)
  logo = models.ImageField(upload_to='logo/', blank=True,
                           validators=[validate_profile])
  description = HTMLField(blank=True)

  def save(self, *args, **kwargs):
    if CustomUser.objects.filter(email=self.user_profile.email).exists():
      if CustomUser.objects.get(email=self.user_profile.email).account_type != 'Recruiter':
        raise ValueError(
            'Email already exists with different account type')

    self.user_profile.first_name = self.company_name
    self.user_profile.save()

    self.user_profile.account_type = 'recruiter'
    geolocator = Nominatim(user_agent="invocamp")
    location = geolocator.geocode(self.location_name, timeout=None)
    point = Point(0, 0)
    print(f"location recruiter: {location}")
    if location is not None:
      self.lat = location.latitude
      self.lng = location.longitude
      point = GEOSGeometry(
          f"POINT({location.longitude} {location.latitude})", srid=4326)
    self.location_coordinates = point
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user_profile.email


class Intern(gis_models.Model):
  user_profile = models.OneToOneField(
      CustomUser,
      primary_key=True,
      on_delete=models.CASCADE,
      related_name='interns',
      related_query_name='interns')
  phone_number = models.CharField(max_length=15, default="123456789123")
  skills = TaggableManager(
      blank=True, related_name='intern_tags')
  description = HTMLField(blank=True, default='Description')
  img_profile = models.ImageField(upload_to='profile_img/', blank=True,
                                  validators=[validate_profile])
  location_name = models.CharField(max_length=100, blank=True, validators=[
      validate_location])
  lat = models.FloatField(blank=True, null=True, default=0)
  lng = models.FloatField(blank=True, null=True, default=0)
  location_coordinates = gis_models.PointField(blank=True, null=True)
  cv = models.FileField(upload_to='cv/', blank=True,
                        validators=[validate_employee_cv])

  def save(self, *args, **kwargs):
    if CustomUser.objects.filter(email=self.user_profile.email).exists():
      if CustomUser.objects.get(email=self.user_profile.email).account_type != 'Intern':
        raise ValidationError(
            'Email already exists with different account type')

    geolocator = Nominatim(user_agent="invocamp-intern")
    location = geolocator.geocode(self.location_name, timeout=None)
    print(f"location intern: {location}")
    point = Point(0, 0)
    if location is not None:
      self.lat = location.latitude
      self.lng = location.longitude
      point = GEOSGeometry(
          f"POINT({location.longitude} {location.latitude})", srid=4326)
    self.location_coordinates = point
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user_profile.email


class Award(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  intern = models.ForeignKey(
      Intern,
      on_delete=models.CASCADE,
      related_name='awards',
      related_query_name='awards')
  title = models.CharField(max_length=255)
  description = HTMLField(blank=True)

  def __str__(self):
    return self.title


class Education(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  intern = models.ForeignKey(
      Intern,
      on_delete=models.CASCADE,
      related_name='educations',
      related_query_name='educations')
  institution = models.CharField(max_length=255)
  field_of_study = models.CharField(max_length=255)
  degree = models.CharField(
      max_length=255, choices=EducationDegree.choices, default=EducationDegree.BACHELOR
  )
  start_date = models.DateField()
  end_date = models.DateField(blank=True, null=True)
  description = HTMLField(blank=True)

  def __str__(self):
    return f"{self.degree} in {self.field_of_study} from {self.institution}"


class OrganizationExperience(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  intern = models.ForeignKey(
      Intern,
      on_delete=models.CASCADE,
      related_name='organization_experiences',
      related_query_name='organization_experiences')
  organization_name = models.CharField(max_length=255)
  position = models.CharField(
      max_length=255, choices=OrganizationPosition.choices, default=OrganizationPosition.MEMBER
  )
  start_date = models.DateField()
  end_date = models.DateField(blank=True, null=True)
  description = HTMLField(blank=True)

  def __str__(self):
    return f"{self.position} at {self.organization_name}"


class WorkExperience(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  intern = models.ForeignKey(
      Intern,
      on_delete=models.CASCADE,
      related_name='work_experiences',
      related_query_name='work_experiences')
  company_name = models.CharField(max_length=255)
  job_title = models.CharField(max_length=255)
  position = models.CharField(
      max_length=255, choices=WorkPosition.choices, default=WorkPosition.INTERN
  )
  start_date = models.DateField()
  end_date = models.DateField(blank=True, null=True)
  description = HTMLField(blank=True)

  def __str__(self):
    return f"{self.job_title} at {self.company_name}"
