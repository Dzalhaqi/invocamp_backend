from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from account_app.serializers.recruiter_serializer import RecruiterSerializer
from account_app.models import Recruiter
from utils.custom_save_document import save_document


class RecruiterUpdateView(UpdateAPIView):
  permission_classes = [IsAuthenticated]
  serializer_class = RecruiterSerializer
  lookup_field = 'user_profile'

  def get_queryset(self):
    return Recruiter.objects.filter(user_profile=self.request.user)

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Update recruiter profile successfully',
    }, status=status.HTTP_200_OK)

  def perform_update(self, serializer):
    recruiter_instance = self.get_object()

    recruiter_instance.company_name = serializer.validated_data.get(
        'company_name', '')
    recruiter_instance.location_name = serializer.validated_data.get(
        'location_name', '')
    recruiter_instance.description = serializer.validated_data.get(
        'description', '')
    recruiter_instance.website = serializer.validated_data.get('website', '')

    save_document(serializer, recruiter_instance, 'logo')

    recruiter_instance.save()
