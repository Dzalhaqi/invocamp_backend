from account_app.models import Intern, Recruiter
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import GEOSGeometry, Point
from django.db import models
from geopy.geocoders import Nominatim
from taggit.managers import TaggableManager


class Status(models.TextChoices):
  PENDING = 'Pending'
  ACCEPTED = 'Accepted'
  REJECTED = 'Rejected'


class VacancyPost(gis_models.Model):
  vacancy_id = models.CharField(primary_key=True, max_length=255, unique=True)
  provider = models.ForeignKey(
      Recruiter, on_delete=models.CASCADE, related_name='vacancy_post')
  title = models.CharField(max_length=255)
  employment_type = models.CharField(max_length=255, blank=True)
  shift = models.CharField(max_length=255, blank=True)
  skills = models.CharField(max_length=255, blank=True)
  published_date = models.DateTimeField(auto_now_add=True)
  updated_date = models.DateTimeField(auto_now=True)
  deadline = models.DateTimeField(blank=True)
  address = models.CharField(max_length=255, blank=True)
  address_coordinates = gis_models.PointField(blank=True, null=True)
  applicants = models.ManyToManyField(
      Intern, related_name='vacancy_post', blank=True)
  description = models.TextField(blank=True)

  def save(self, *args, **kwargs):
    self.provider_id = self.provider.user_id
    if self.address:
      geolocator = Nominatim(user_agent="vacancy-post")
      location = geolocator.geocode(self.address)
      self.address_coordinates = Point(
          location.longitude, location.latitude, srid=4326)
    else:
      self.address_coordinates = Point(0, 0, srid=4326)
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.title} - {self.provider.company_name}"


class VacancyApplication(gis_models.Model):
  applicant = models.ForeignKey(
      Intern, on_delete=models.CASCADE, related_name='vacancy_application')
  vacancy = models.ForeignKey(
      VacancyPost, on_delete=models.CASCADE, related_name='vacancy_application')
  cover_letter = models.TextField(blank=True)
  resume = models.FileField(upload_to='resumes/')
  applied_date = models.DateTimeField(auto_now_add=True)
  status = models.CharField(
      max_length=255, choices=Status.choices, default=Status.PENDING)
  note = models.TextField(blank=True)

  def __str__(self):
    return f"{self.applicant.email} - {self.vacancy.title}"
