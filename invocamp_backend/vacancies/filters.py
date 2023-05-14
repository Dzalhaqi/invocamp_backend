from django_filters import rest_framework as filters
from vacancies.models import VacancyPost


class VacancyFilter(filters.FilterSet):
  title = filters.CharFilter(field_name='title', lookup_expr='icontains')
  address = filters.CharFilter(field_name='address', lookup_expr='icontains')
  skills = filters.CharFilter(field_name='skills', lookup_expr='icontains')
  employment_type = filters.CharFilter(
      field_name='employment_type', lookup_expr='icontains')
  work_type = filters.CharFilter(
      field_name='work_type', lookup_expr='icontains')
  education_level = filters.CharFilter(
      field_name='education_level', lookup_expr='icontains')

  class Meta:
    model = VacancyPost
    fields = ('title', 'address', 'skills', 'employment_type',
              'work_type', 'education_level')
