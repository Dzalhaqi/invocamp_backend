from django import template
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

register = template.Library()


@register.simple_tag
@api_view(['GET'])
def email_verified_response():
  response_data = {
      'message': 'Error',
      'status': status.HTTP_400_BAD_REQUEST,
      'details': 'invalid url'
  }
  return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
