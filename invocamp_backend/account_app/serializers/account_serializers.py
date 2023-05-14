from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from account_app.models import AccountType, CustomUser, Recruiter, Intern
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from allauth.account.models import EmailAddress


class CustomUserRegisterSerializer(serializers.Serializer):
  first_name = serializers.CharField(required=True)
  account_type = serializers.ChoiceField(
      choices=AccountType.choices, default=AccountType.INTERN)
  email = serializers.EmailField(required=True)
  password = serializers.CharField(required=True, write_only=True)
  password_confirmation = serializers.CharField(required=True, write_only=True)

  def validate_password(self, password):
    validation_message = []
    if len(password) < 8:
      validation_message.append(
          'Password must be at least 8 characters long.')
    if not any(char.isdigit() for char in password):
      validation_message.append(
          'Password must contain at least 1 number.')
    if not any(char.isupper() for char in password):
      validation_message.append(
          'Password must contain at least 1 uppercase letter.')
    if not any(char.islower() for char in password):
      validation_message.append(
          'Password must contain at least 1 lowercase letter.')
    if not any(char in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '='] for char in password):
      validation_message.append(
          'Password must contain at least 1 special character.')
    if password != self.initial_data.get('password_confirmation'):
      validation_message.append('Passwords do not match.')

    if len(validation_message) > 0:
      raise ValidationError(validation_message)

    return password

  def create(self, validated_data):
    last_name = validated_data.get('last_name', '')
    user = CustomUser(
        email=validated_data['email'],
        account_type=validated_data['account_type'],
        first_name=validated_data['first_name'],
        last_name=last_name,
    )

    password = validated_data['password']
    user.set_password(password)
    user.save()

    if validated_data['account_type'] == AccountType.INTERN:
      intern = Intern.objects.create(user_profile=user)
      intern.save()

    elif validated_data['account_type'] == AccountType.RECRUITER:
      recruiter = Recruiter.objects.create(
          user_profile=user, company_name=validated_data['first_name'] + ' ' + last_name)
      recruiter.save()

    return user


class CustomUserLoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField(write_only=True)

  def validate(self, attrs):
    email = attrs.get('email')
    password = attrs.get('password')

    try:
      email_address = EmailAddress.objects.get(email=email)
      user = authenticate(email=email_address, password=password)

      attrs['user'] = user
      return attrs

    except Exception as e:
      raise AuthenticationFailed


class EmailVerificationSerializer(serializers.Serializer):
  email = serializers.EmailField()
