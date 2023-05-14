from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from rest_framework import serializers
from account_app.models import Award, Education, OrganizationExperience, Intern, WorkExperience, CustomUser


class AwardsSerializer(serializers.ModelSerializer):
  class Meta:
    model = Award
    exclude = ('intern',)


class EducationSerializer(serializers.ModelSerializer):
  class Meta:
    model = Education
    exclude = ('intern',)


class WorkExperienceSerializer(serializers.ModelSerializer):
  class Meta:
    model = WorkExperience
    exclude = ('intern',)


class OrganizationExperienceSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrganizationExperience
    exclude = ('intern',)


class InternSerializer(TaggitSerializer, serializers.ModelSerializer):
  first_name = serializers.CharField(source='user_profile.first_name')
  last_name = serializers.CharField(
      source='user_profile.last_name', required=False)
  account_type = serializers.CharField(
      source='user_profile.account_type', required=False)
  email = serializers.CharField(source='user_profile.email', read_only=True)
  awards = AwardsSerializer(many=True, required=False)
  educations = EducationSerializer(many=True, required=False)
  work_experiences = WorkExperienceSerializer(many=True, required=False)
  organization_experiences = OrganizationExperienceSerializer(
      many=True, required=False)
  skills = TagListSerializerField()

  class Meta:
    model = Intern
    fields = ('user_profile', 'first_name', 'last_name', 'email', 'account_type', 'phone_number', 'skills', 'description',
              'img_profile', 'location_name', 'lat', 'lng', 'location_coordinates', 'cv', 'awards', 'educations', 'work_experiences', 'organization_experiences',)
    read_only_fields = ('user_profile', 'lat', 'lng', 'account_type',
                        'location_coordinates', 'email')
    extra_kwargs = {
        'first_name': {'required': True},
        'location_name': {'required': True},
        'cv': {'required': True},
        'skills': {'required': True},
        'description': {'required': True},
    }
