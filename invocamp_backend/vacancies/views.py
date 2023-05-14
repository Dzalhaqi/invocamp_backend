from account_app.models import Intern, Recruiter
from vacancies.filters import VacancyFilter
from django.db.models.signals import post_save

from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError

from vacancies.models import VacancyApplication, VacancyPost
from vacancies.serializers import (VacancyPostDetailSerializer, VacancyPostListSerializer,
                                   VacancyPostDetailRecruiterSerializer, VacancyApplicationSerializer, VacancyApplicationRecruiterSerializer, VacancyApplicationInternSerializer)
from utils.permission import IsRecruiter, IsIntern
from utils.custom_exceptions import AlreadyApplied, VacancyApplicationNotFound, VacancyNotFound


class VacancyPostedListAPIView(ListAPIView):
  queryset = VacancyPost.objects.all()
  permission_classes = [IsAuthenticated, IsRecruiter]
  serializer_class = VacancyPostListSerializer

  def get_queryset(self):
    return VacancyPost.objects.filter(provider__user_profile=self.request.user)

  def list(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    serializer = self.get_serializer(queryset, many=True)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve data list',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


class VacancyPostedRetrieveAPIView(RetrieveAPIView):
  queryset = VacancyPost.objects.all()
  permission_classes = [IsAuthenticated, IsRecruiter]
  serializer_class = VacancyPostDetailRecruiterSerializer

  def get_queryset(self):
    return VacancyPost.objects.filter(provider__user_profile=self.request.user)

  def get_object(self):
    try:
      return VacancyPost.objects.get(pk=self.kwargs['vacancy_id'])
    except VacancyPost.DoesNotExist:
      raise VacancyNotFound

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.provider.user_profile != request.user:
      raise VacancyNotFound

    serializer = self.get_serializer(instance)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve data',
        'data': serializer.data
    })


class VacancyPostViewSet(ModelViewSet):
  permission_classes_by_action = {
      'create': [IsAuthenticated, IsRecruiter],
      'update': [IsAuthenticated, IsRecruiter],
      'destroy': [IsAuthenticated, IsRecruiter],
      'list': [AllowAny],
      'retrieve': [AllowAny],
  }

  def get_permissions(self):
    try:
      return [permission() for permission in self.permission_classes_by_action[self.action]]
    except KeyError:
      return [permission() for permission in self.permission_classes]

  def get_serializer_class(self):
    if self.action == 'list':
      return VacancyPostListSerializer
    return VacancyPostDetailSerializer

  def perform_create(self, serializer):
    recruiter_instance = Recruiter(user_profile=self.request.user)
    serializer.save(provider=recruiter_instance)

  def get_queryset(self):
    queryset = VacancyPost.objects.all()
    filterset = VacancyFilter(self.request.GET, queryset=queryset)
    return filterset.qs

  def get_object(self):
    try:
      return VacancyPost.objects.get(pk=self.kwargs['pk'])
    except VacancyPost.DoesNotExist:
      raise VacancyNotFound

  def list(self, request, *args, **kwargs):
    queryset = self.get_queryset()
    serializer = self.get_serializer(queryset, many=True)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve data list',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve data',
        'data': serializer.data
    })

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      self.perform_create(serializer)

      skills_data = request.data.get('skills', [])
      skills_data = skills_data.strip().split(',')
      skills_data = list(filter(lambda x: len(x.strip()) != 0, skills_data))

      vacancy_post_instance = self.get_object()
      vacancy_post_instance.skills.clear()

      for skill in skills_data:
        vacancy_post_instance.skills.add(
            skill.strip().replace("'", ''))

      return Response({
          'success': True,
          'code': 200,
          'detail': 'Successfully create data',
      }, status=status.HTTP_201_CREATED)

    raise ValidationError(serializer.errors)

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.provider.user_profile.id != request.user.id:
      raise PermissionDenied

    serializer = self.get_serializer(instance, data=request.data)
    if serializer.is_valid():
      self.perform_update(serializer)

      skills_data = request.data.get('skills', [])
      skills_data = skills_data.strip().split(',')
      skills_data = list(filter(lambda x: len(x.strip()) != 0, skills_data))

      vacancy_post_instance = self.get_object()
      vacancy_post_instance.skills.clear()

      for skill in skills_data:
        vacancy_post_instance.skills.add(
            skill.strip().replace("'", ''))

      return Response({
          'success': True,
          'code': 200,
          'detail': 'Successfully update data',
      }, status=status.HTTP_200_OK)

    raise ValidationError(serializer.errors)

  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.provider.user_profile.id != request.user.id:
      raise PermissionDenied

    instance.delete()
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully delete data'
    }, status=status.HTTP_200_OK)


class VacancyApplicationInternViewSet(ModelViewSet):
  serializer_class = VacancyApplicationInternSerializer
  permission_classes = [IsAuthenticated, IsIntern]

  def get_queryset(self):
    intern_instance = Intern(user_profile=self.request.user)
    return VacancyApplication.objects.filter(
        applicant=intern_instance)

  def get_object(self):
    try:
      return self.get_queryset().get(pk=self.kwargs['pk'])
    except VacancyApplication.DoesNotExist:
      raise VacancyApplicationNotFound

  def list(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    serializer = self.get_serializer(queryset, many=True)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve application list data',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    serializer = self.get_serializer(instance)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve application data',
        'data': serializer.data
    })

  def create(self, request, *args, **kwargs):
    vacancy_id = request.data.get('vacancy_id')

    try:
      vacancy = VacancyPost.objects.get(pk=vacancy_id)
    except VacancyPost.DoesNotExist:
      raise VacancyNotFound

    intern_instance = Intern(user_profile=self.request.user)

    if VacancyApplication.objects.filter(
            applicant=intern_instance,
            vacancy=vacancy).exists():
      raise AlreadyApplied

    data = request.data.copy()
    data['vacancy'] = vacancy.id
    data['applicant'] = intern_instance

    serializer = self.get_serializer(data=data)

    if serializer.is_valid():
      self.perform_create(serializer)
      return Response({
          'success': True,
          'code': 200,
          'detail': 'Successfully create data',
      }, status=status.HTTP_201_CREATED)

    raise ValidationError(serializer.errors)

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.applicant.user_profile.id != request.user.id:
      raise VacancyApplicationNotFound

    data = request.data.copy()
    data['vacancy'] = instance.vacancy.id
    data['applicant'] = instance.applicant

    serializer = self.get_serializer(instance, data=data)
    if serializer.is_valid():
      self.perform_update(serializer)
      post_save.send(sender=VacancyApplication, instance=instance)
      return Response({
          'success': True,
          'code': 200,
          'detail': 'Successfully update data',
      }, status=status.HTTP_200_OK)

    raise ValidationError(serializer.errors)

  def destroy(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.applicant.user_profile.id != request.user.id:
      raise VacancyApplicationNotFound

    instance.delete()
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully delete data'
    }, status=status.HTTP_200_OK)


class VacancyPostedApplicationsListAPIView(ListAPIView):
  serializer_class = VacancyApplicationInternSerializer
  permission_classes = [IsAuthenticated, IsRecruiter]

  def get_queryset(self):
    recruiter_instance = Recruiter(user_profile=self.request.user)
    return VacancyApplication.objects.filter(
        vacancy__provider=recruiter_instance)

  def list(self, request, *args, **kwargs):
    vacancy_id = self.kwargs.get('vacancy_id')

    try:
      vacancy = VacancyPost.objects.get(id=vacancy_id)
    except VacancyPost.DoesNotExist:
      raise VacancyNotFound

    if vacancy.provider.user_profile.id != request.user.id:
      raise VacancyNotFound

    queryset = self.filter_queryset(self.get_queryset().filter(
        vacancy=vacancy))
    serializer = self.get_serializer(queryset, many=True)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve application list data list',
        'data': serializer.data
    }, status=status.HTTP_200_OK)


class VacancyPostedApplicationsRetrieveAPIView(RetrieveAPIView):
  serializer_class = VacancyApplicationInternSerializer
  permission_classes = [IsAuthenticated, IsRecruiter]

  def get_queryset(self):
    recruiter_instance = Recruiter(user_profile=self.request.user)
    return VacancyApplication.objects.filter(
        vacancy__provider=recruiter_instance)

  def get_object(self):
    try:
      return self.get_queryset().get(pk=self.kwargs['vacancy_id'])
    except VacancyApplication.DoesNotExist:
      raise VacancyApplicationNotFound

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()

    serializer = self.get_serializer(instance)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve vacancy posted application data',
        'data': serializer.data
    })


class VacancyPostedApplicationsUpdateAPIView(UpdateAPIView):
  serializer_class = VacancyApplicationInternSerializer
  permission_classes = [IsAuthenticated, IsRecruiter]

  def get_queryset(self):
    recruiter_instance = Recruiter(user_profile=self.request.user)
    return VacancyApplication.objects.filter(
        vacancy__provider=recruiter_instance)

  def get_object(self):
    try:
      return self.get_queryset().get(pk=self.kwargs['vacancy_id'])
    except VacancyApplication.DoesNotExist:
      raise VacancyApplicationNotFound

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.vacancy.provider.user_profile.id != request.user.id:
      raise PermissionDenied

    data = request.data.copy()
    data['vacancy'] = instance.vacancy.id
    data['applicant'] = instance.applicant

    serializer = self.get_serializer(instance, data=data)
    if serializer.is_valid():
      self.perform_update(serializer)
      return Response({
          'success': True,
          'code': 200,
          'detail': 'Successfully update application data',
      }, status=status.HTTP_200_OK)

    raise ValidationError(serializer.errors)


class VacancyPostedApplicationsRetrieveUpdateAPIView(RetrieveUpdateAPIView):
  permission_classes = [IsAuthenticated, IsRecruiter]

  def get_serializer_class(self):
    if self.request.method == 'GET':
      return VacancyApplicationInternSerializer
    elif self.request.method == 'PUT':
      return VacancyApplicationRecruiterSerializer

  def get_queryset(self):
    recruiter_instance = Recruiter(user_profile=self.request.user)
    return VacancyApplication.objects.filter(
        vacancy__provider=recruiter_instance)

  def get_object(self):
    try:
      return self.get_queryset().get(pk=self.kwargs['application_id'])
    except VacancyApplication.DoesNotExist:
      raise VacancyApplicationNotFound

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()

    vacancy_id = self.kwargs.get('vacancy_id')
    if instance.vacancy.id != vacancy_id:
      raise VacancyNotFound

    serializer = self.get_serializer(instance)
    return Response({
        'success': True,
        'code': 200,
        'detail': 'Successfully retrieve vacancy posted application data',
        'data': serializer.data
    })

  def update(self, request, *args, **kwargs):
    instance = self.get_object()
    if instance.vacancy.provider.user_profile.id != request.user.id:
      raise PermissionDenied

    data = request.data.copy()
    data['vacancy'] = instance.vacancy.id
    data['applicant'] = instance.applicant

    if instance.vacancy.id != self.kwargs.get('vacancy_id'):
      raise VacancyNotFound

    serializer = self.get_serializer(instance, data=data)
    if serializer.is_valid():
      self.perform_update(serializer)
      return Response({
          'success': True,
          'code': 200,
          'detail': 'Successfully update application data',
      }, status=status.HTTP_200_OK)

    raise ValidationError(serializer.errors)
