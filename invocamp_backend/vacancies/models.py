from account_app.models import Intern, Recruiter
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import models
from geopy.geocoders import Nominatim
from taggit.managers import TaggableManager
from tinymce.models import HTMLField
import uuid


class Status(models.TextChoices):
  PENDING = 'Pending'
  ACCEPTED = 'Accepted'
  REJECTED = 'Rejected'


class EmploymentType(models.TextChoices):
  FULL_TIME = 'Full Time'
  PART_TIME = 'Part Time'
  CONTRACT = 'Contract'
  INTERNSHIP = 'Internship'
  FREELANCE = 'Freelance'
  TEMPORARY = 'Temporary'
  VOLUNTEER = 'Volunteer'


class WorkType(models.TextChoices):
  REMOTE = 'Remote'
  ON_SITE = 'On Site'
  HYBRID = 'Hybrid'


class educationLevel(models.TextChoices):
  HIGH_SCHOOL = 'High School'
  DIPLOMA = 'Diploma'
  BACHELOR = 'Bachelor'
  MASTER = 'Master'
  DOCTORATE = 'Doctorate'


class VacancyPost(gis_models.Model):
  id = models.AutoField(primary_key=True, editable=False)
  provider = models.ForeignKey(
      Recruiter,
      on_delete=models.CASCADE,
      related_name='vacancy_posts',
      related_query_name='vacancy_posts')
  title = models.CharField(max_length=255)
  employment_type = models.CharField(
      max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME
  )
  work_type = models.CharField(
      max_length=20, choices=WorkType.choices, default=WorkType.ON_SITE
  )
  education_level = models.CharField(
      max_length=20, choices=educationLevel.choices, default=educationLevel.BACHELOR
  )
  skills = TaggableManager(blank=True, related_name='vacancy_post_tags')
  salary = models.PositiveIntegerField(blank=True, default=0)
  published_date = models.DateTimeField(auto_now_add=True)
  updated_date = models.DateTimeField(auto_now=True)
  deadline = models.DateTimeField(blank=True, null=True)
  address = models.CharField(max_length=255, blank=True)
  lat = models.FloatField(blank=True, null=True, default=0)
  lng = models.FloatField(blank=True, null=True, default=0)
  address_coordinates = gis_models.PointField(blank=True, null=True)
  applicants = models.ManyToManyField(
      Intern, related_name='vacancy_post', blank=True)
  description = HTMLField(blank=True)

  def save(self, *args, **kwargs):
    if self.address:
      geolocator = Nominatim(user_agent="vacancy-post", timeout=None)
      location = geolocator.geocode(self.address)
      self.lat = location.latitude
      self.lng = location.longitude
      self.address_coordinates = Point(
          location.longitude, location.latitude, srid=4326)
    else:
      self.address_coordinates = Point(0, 0, srid=4326)
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.title} - {self.provider.company_name}"


class VacancyApplication(gis_models.Model):
  id = models.AutoField(primary_key=True, editable=False)
  applicant = models.ForeignKey(
      Intern,
      on_delete=models.CASCADE,
      related_name='vacancy_applications',
      related_query_name='vacancy_applications')
  vacancy = models.ForeignKey(
      VacancyPost,
      on_delete=models.CASCADE,
      related_name='vacancy_applications',
      related_query_name='vacancy_applications')
  cover_letter = models.TextField(blank=True)
  cv = models.FileField(default=None)
  applied_date = models.DateTimeField(auto_now_add=True)
  updated_date = models.DateTimeField(auto_now=True)
  status = models.CharField(
      max_length=255, choices=Status.choices, default=Status.PENDING)
  note = HTMLField(blank=True)

  def save(self, *args, **kwargs):
    self.cv = self.applicant.cv
    if self.cv == None:
      raise Exception('CV is not uploaded')

    # if self.applicant.vacancy_applications.filter(vacancy=self.vacancy).exists():
    #   raise Exception('You have already applied for this vacancy')

    if self.applicant.vacancy_applications.filter(vacancy=self.vacancy, status__in=[Status.ACCEPTED, Status.PENDING]).exists():
      raise Exception('You have already applied for this vacancy')

    if self.applicant == self.vacancy.provider:
      raise Exception('You cannot apply for your own vacancy')

    if not self.vacancy.applicants.filter(user_profile=self.applicant.user_profile).exists():
      self.vacancy.applicants.add(self.applicant)

    super().save()

  def __str__(self):
    return f"{self.applicant} - {self.vacancy.title}"
