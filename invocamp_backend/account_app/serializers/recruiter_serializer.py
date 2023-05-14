
from rest_framework import serializers
from account_app.models import Recruiter


class RecruiterSerializer(serializers.ModelSerializer):
  email = serializers.CharField(source='user_profile.email', read_only=True)
  account_type = serializers.CharField(
      source='user_profile.account_type', required=False)

  class Meta:
    model = Recruiter
    fields = ('user_profile', 'account_type', 'company_name', 'email', 'website', 'location_name',
              'lat', 'lng', 'location_coordinates', 'logo', 'description',)
    read_only_fields = ('user_profile', 'lat', 'lng', 'account_type',
                        'location_coordinates', 'email')
    extra_kwargs = {
        'company_name': {'required': True},
        'website': {'required': True},
        'location_name': {'required': True},
        'description': {'required': True},
    }
