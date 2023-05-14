import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from account_app.serializers.intern_serializer import InternSerializer, AwardsSerializer
from account_app.models import Intern
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import slugify
from utils.custom_save_document import save_document


class InternUpdateView(UpdateAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = InternSerializer
  lookup_field = 'user_profile'

  def get_queryset(self):
    return Intern.objects.filter(user_profile=self.request.user)

  def update(self, request, *args, **kwargs):
    instance = self.get_object()

    serializer = self.get_serializer(instance, data=request.data)
    serializer.is_valid(raise_exception=True)

    awards_data = serializer.validated_data.get('awards', [])
    for award_data in awards_data:
      award_serializer = AwardsSerializer(data=award_data)
      if award_serializer.is_valid():
        award_serializer.save(intern=instance)

    self.perform_update(serializer)

    return Response({
        'success': True,
        'code': 200,
        'detail': 'Update intern profile successfully',
    }, status=status.HTTP_200_OK)

  def perform_update(self, serializer):
    intern_instance = self.get_object()

    custom_user_instance = intern_instance.user_profile
    custom_user_instance.first_name = serializer.validated_data['user_profile']['first_name']
    custom_user_instance.last_name = serializer.validated_data['user_profile'].get(
        'last_name', '')
    custom_user_instance.save()

    intern_instance.phone_number = serializer.validated_data.get(
        'phone_number', '')
    intern_instance.location_name = serializer.validated_data.get(
        'location_name', '')
    intern_instance.description = serializer.validated_data.get(
        'description', '')

    skills_data = serializer.validated_data.pop('skills', [])
    skills_data = skills_data[0].replace("'", "").split(', ')
    intern_instance.skills.clear()

    for skill in skills_data:
      intern_instance.skills.add(skill)

    save_document(serializer, intern_instance, 'cv')
    save_document(serializer, intern_instance, 'img_profile')

    intern_instance.save()
