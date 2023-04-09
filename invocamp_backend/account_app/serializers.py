from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import AccountType, CustomUser
from django.utils.translation import gettext_lazy as _
from allauth.utils import email_address_exists
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import CustomUser, Recruiter, Intern

User = get_user_model()


class RecruiterSerializer(serializers.ModelSerializer):
  class Meta:
    model = Recruiter
    fields = '__all__'


class InternSerializer(serializers.ModelSerializer):
  class Meta:
    model = Intern
    fields = '__all__'


class CustomUserSignupSerializer(serializers.Serializer):
  first_name = serializers.CharField(required=True)
  last_name = serializers.CharField(required=False, default='')
  account_type = serializers.ChoiceField(
      choices=AccountType.choices, default=AccountType.INTERN)
  email = serializers.EmailField(required=True)
  password = serializers.CharField(required=True, write_only=True)
  password_confirmation = serializers.CharField(required=True, write_only=True)

  def validate_email(self, email):
    if email and email_address_exists(email):
      raise serializers.ValidationError('Email address already exists.')
    return email

  def validate_password1(self, password):
    min_length = 8
    if len(password) < min_length:
      raise serializers.ValidationError(
          f'Password must be at least {min_length} characters.')
    try:
      validate_password(password)
    except ValidationError as e:
      raise serializers.ValidationError(str(e))
    return password

  def validate(self, data):
    if data['password'] != data['password_confirmation']:
      raise serializers.ValidationError('Passwords doesn\'t match')
    return data

  def create(self, validated_data):
    user = CustomUser(
        email=validated_data['email'],
        account_type=validated_data['account_type'],
        first_name=validated_data['first_name'],
        last_name=validated_data.get('last_name'),
    )

    password = validated_data['password']
    user.set_password(password)
    user.save()

    if validated_data['account_type'] == AccountType.INTERN:
      intern = Intern.objects.create(user_profile=user)
      intern.save()

    if validated_data['account_type'] == AccountType.RECRUITER:
      recruiter = Recruiter.objects.create(
          user_profile=user, company_name=validated_data['first_name'] + ' ' + validated_data['last_name'])
      recruiter.save()

    return user


class CustomUserLoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True)

  def validate(self, attrs):
    email = attrs.get('email')
    password = attrs.get('password')

    if email and password:
      user = authenticate(email=email, password=password)
      if not user:
        raise serializers.ValidationError('Invalid email or password')

      attrs['user'] = user

    return attrs


class EmailVerificationSerializer(serializers.Serializer):
  key = serializers.CharField()


class CurrentUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = CustomUser
    fields = [
        'id',
        'first_name',
        'last_name',
        'email',
        'account_type',
    ]
