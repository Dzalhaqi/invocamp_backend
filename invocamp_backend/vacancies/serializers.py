from rest_framework import serializers
from vacancies.models import VacancyPost, VacancyApplication
from taggit.serializers import TagListSerializerField, TaggitSerializer


class VacancyPostListSerializer(serializers.ModelSerializer):
  provider_name = serializers.CharField(
      source='provider.company_name', read_only=True)
  provider_logo = serializers.ImageField(
      source='provider.logo', read_only=True)
  skills = TagListSerializerField()

  class Meta:
    model = VacancyPost
    fields = ('id', 'title', 'employment_type', 'work_type', 'skills', 'salary', 'lat', 'lng', 'education_level',
              'description', 'address', 'provider', 'updated_date', 'published_date', 'deadline', 'provider_name', 'provider_logo')


class VacancyPostDetailSerializer(serializers.ModelSerializer):
  provider_name = serializers.CharField(
      source='provider.company_name', read_only=True)
  provider_logo = serializers.ImageField(
      source='provider.logo', read_only=True)
  skills = TagListSerializerField()

  class Meta:
    model = VacancyPost
    # exclude = ('applicants',)
    fields = ('id', 'title', 'employment_type', 'work_type', 'skills', 'salary', 'lat', 'lng', 'education_level',
              'description', 'address', 'provider', 'updated_date', 'published_date', 'deadline', 'provider_name', 'provider_logo')
    read_only_fields = ('id', 'provider', 'published_date', 'updated_date',
                        'lat', 'lng', 'address_coordinates', 'provider_name', 'provider_logo')
    extra_kwargs = {
        'title': {'required': True},
        'employment_type': {'required': True},
        'work_type': {'required': True},
        'skills': {'required': True},
        'description': {'required': True},
        'address': {'required': True},
        'location_name': {'required': True},
        'salary': {'required': True},
    }


class VacancyPostDetailRecruiterSerializer(serializers.ModelSerializer):
  class Meta:
    model = VacancyPost
    fields = '__all__'


class VacancyApplicationSerializer(serializers.ModelSerializer):
  class Meta:
    model = VacancyApplication
    fields = '__all__'
    read_only_fields = ('id', 'vacancy', 'applicant', 'status',
                        'applied_date', 'updated_date', 'cv')
    extra_kwargs = {
        'vacancy': {'required': True},
        'applicant': {'required': True},
        'status': {'required': True},
        'cv': {'required': True},
    }


class VacancyApplicationRecruiterSerializer(serializers.ModelSerializer):
  class Meta:
    model = VacancyApplication
    fields = '__all__'
    read_only_fields = ('id', 'vacancy', 'applicant', 'cover_letter',
                        'applied_date', 'updated_date', 'cv')


class VacancyApplicationInternSerializer(serializers.ModelSerializer):
  vacancy_name = serializers.CharField(
      source='vacancy.title', read_only=True)
  applicant_name = serializers.SerializerMethodField()

  def get_applicant_name(self, obj):
    full_name = obj.applicant.user_profile.first_name + \
        ' ' + obj.applicant.user_profile.last_name
    return full_name.strip()

  class Meta:
    model = VacancyApplication
    fields = '__all__'
    read_only_fields = ('id', 'status', 'note',
                        'applied_data', 'update_date', 'vacancy_name', 'applicant_name')
