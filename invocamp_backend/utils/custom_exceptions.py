from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):

  response = exception_handler(exc, context)
  exception_class = exc.__class__.__name__

  if exception_class == 'ValidationError':
    response.data = {
        "error": True,
        "code": 400,
        "detail": response.data
    }

  if exception_class == 'NotFound':
    response.data = {
        "error": True,
        "code": 404,
        "detail": "Resource not found"
    }

  if exception_class == 'AuthenticationFailed':
    response.data = {
        "error": True,
        "code": 401,
        "detail": "Invalid credentials"
    }

  if exception_class == 'NotAuthenticated':
    response.data = {
        "error": True,
        "code": 401,
        "detail": "Authentication credentials were not provided"
    }

  if exception_class == 'PermissionDenied':
    response.data = {
        "error": True,
        "code": 403,
        "detail": "You do not have permission to perform this action"
    }

  if exception_class == 'NoReverseMatch':
    response.data = {
        "error": True,
        "code": 404,
        "detail": "Resource not found"
    }

  if exception_class == 'InvalidToken':
    response.data = {
        "error": True,
        "code": 401,
        "detail": "Invalid token"
    }

  if exception_class == 'AlreadyApplied':
    response.data = {
        "error": True,
        "code": 400,
        "detail": "You have already applied for this vacancy."
    }

  if exception_class == 'VacancyNotFound':
    response.data = {
        "error": True,
        "code": 404,
        "detail": "Vacancy not found."
    }

  if exception_class == 'VacancyApplicationNotFound':
    response.data = {
        "error": True,
        "code": 404,
        "detail": "Vacancy application not found."
    }

  return response


class AlreadyApplied(APIException):
  status_code = 400
  default_detail = 'You have already applied for this vacancy.'
  default_code = 'already_applied'


class VacancyNotFound(APIException):
  status_code = 404
  default_detail = 'Vacancy not found.'
  default_code = 'vacancy_not_found'


class VacancyApplicationNotFound(APIException):
  status_code = 404
  default_detail = 'Vacancy application not found.'
  default_code = 'vacancy_application_not_found'
