from geopy.exc import GeocoderTimedOut
from django.core.exceptions import ValidationError
from geopy.geocoders import Nominatim
import os


def validate_location(value):
  """
  Validates the location name entered by the company, and raises a
  ValidationError if the location is not found by the geolocator.
  """
  try:
    geolocator = Nominatim(user_agent="invocamp")
    location = geolocator.geocode(value)
    if not location:
      raise ValidationError(
          "Invalid location: Could not find location matching the name entered.")
  except GeocoderTimedOut:
    raise ValidationError(
        "Geocoder service timed out. Please try again later.")
  except Exception:
    raise ValidationError(
        "An error occurred while trying to validate the location. Please try again later.")


def validate_employee_cv(value):
  """
  Validates the CV uploaded by the employee, and raises a ValidationError
  if the file size is greater than 5 MB and file not in pdf format.
  """
  file_size = value.size
  if file_size > 5 * 1024 * 1024:
    raise ValidationError("The maximum file size allowed is 5 MB.")

  ext = os.path.splitext(value.name)[1]
  if ext.lower() != '.pdf':
    raise ValidationError('File must be a PDF.')
