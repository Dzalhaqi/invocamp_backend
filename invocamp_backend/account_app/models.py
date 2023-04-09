from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import models
from geopy.geocoders import Nominatim
from taggit.managers import TaggableManager
from tinymce.models import HTMLField

from .validations import validate_employee_cv, validate_location


class AccountType(models.TextChoices):
  RECRUITER = 'recruiter'
  INTERN = 'intern'


class CustomUserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError('The Email field must be set')
    email = self.normalize_email(email)
    user = self.model(
        email=email, **extra_fields)
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
  user_profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
  user_id = models.IntegerField(primary_key=True, editable=False)
  company_name = models.CharField(max_length=255, default="Company Name")
  category = TaggableManager(blank=True)
  website = models.URLField(blank=True)
  location_name = models.CharField(max_length=255, blank=True, validators=[
      validate_location])
  location_coordinates = gis_models.PointField(blank=True, null=True)
  logo = models.ImageField(upload_to='logo/', blank=True)
  description = HTMLField(blank=True)

  def save(self, *args, **kwargs):
    self.user_id = self.user_profile.id
    self.user_profile.account_type = 'recruiter'
    geolocator = Nominatim(user_agent="invocamp")
    location = geolocator.geocode(self.location_name)
    point = Point(0, 0)
    print(f"location recruiter: {location}")
    if location is not None:
      point = GEOSGeometry(
          f"POINT({location.longitude} {location.latitude})", srid=4326)
    self.location_coordinates = point
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user_profile.email


class Intern(gis_models.Model):
  user_profile = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
  user_id = models.IntegerField(primary_key=True, editable=False)
  phone_number = models.CharField(max_length=15, default="123456789123")
  education = HTMLField(blank=True)
  organization_experience = HTMLField(blank=True)
  work_experience = HTMLField(blank=True)
  skills = TaggableManager(blank=True)
  awards = HTMLField(blank=True)
  img_profile = models.ImageField(upload_to='profile_img/', blank=True)
  location_name = models.CharField(max_length=100, blank=True, validators=[
      validate_location])
  location_coordinates = gis_models.PointField(blank=True, null=True)
  cv = models.FileField(upload_to='cv/', blank=True,
                        validators=[validate_employee_cv])

  def save(self, *args, **kwargs):
    self.user_id = self.user_profile.id
    geolocator = Nominatim(user_agent="invocamp-intern")
    location = geolocator.geocode(self.location_name)
    print(f"location intern: {location}")
    point = Point(0, 0)
    if location is not None:
      point = GEOSGeometry(
          f"POINT({location.longitude} {location.latitude})", srid=4326)
    self.location_coordinates = point
    super().save(*args, **kwargs)

  def __str__(self):
    return self.user_profile.email
