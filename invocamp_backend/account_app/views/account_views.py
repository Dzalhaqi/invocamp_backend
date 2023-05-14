from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.html import strip_tags
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.account.models import EmailConfirmationHMAC
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework import permissions
from dj_rest_auth.utils import jwt_encode
from allauth.socialaccount.models import SocialAccount
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from urllib.parse import urlencode

import requests
from allauth.account.utils import complete_signup, send_email_confirmation
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import (SocialAccount, SocialApp,
                                          SocialLogin, SocialToken)
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import (OAuth2CallbackView,
                                                          OAuth2LoginView)
from dj_rest_auth.registration.views import (ConfirmEmailView, RegisterView,
                                             SocialConnectView, ResendEmailVerificationView,
                                             SocialLoginView, VerifyEmailView)
from dj_rest_auth.views import (LogoutView, PasswordChangeView,
                                PasswordResetConfirmView, PasswordResetView)

from allauth.account.models import EmailAddress

from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from account_app.models import Intern, Recruiter
from account_app.serializers.account_serializers import (CustomUserLoginSerializer,
                                                         CustomUserRegisterSerializer, EmailVerificationSerializer)

from account_app.serializers.intern_serializer import InternSerializer
from account_app.serializers.recruiter_serializer import RecruiterSerializer


class GoogleLogin(SocialLoginView):
  adapter_class = GoogleOAuth2Adapter
  permission_classes = [permissions.AllowAny]
  callback_url = 'http://localhost:8000/accounts/google/login/callback/'

  def get(self, request):
    code = request.GET.get('code')
    if code:
      # Exchange the code for an access token and ID token
      data = {
          'code': code,
          'client_id': settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID,
          'client_secret': settings.SOCIAL_AUTH_GOOGLE_SECRET,
          'redirect_uri': self.callback_url,
          'grant_type': 'authorization_code'
      }
      response = requests.post(
          'https://www.googleapis.com/oauth2/v4/token', data=data)
      token_data = response.json()

      # Use the ID token to retrieve user info
      headers = {'Authorization': f'Bearer {token_data["id_token"]}'}
      response = requests.get(
          'https://www.googleapis.com/oauth2/v1/userinfo', headers=headers)
      user_data = response.json()

      # Use the access token to log the user in
      self.serializer = self.get_serializer(
          data={'access_token': token_data['access_token']})
      self.serializer.is_valid(raise_exception=True)
      self.login()

      # Return the JWT token and user data
      return JsonResponse({'token': self.get_response_data(request.user)['token'], 'user': user_data})
    else:
      # Handle error case when no code is present
      return JsonResponse({'error': 'No authorization code provided.'}, status=400)


class GoogleLoginView(APIView):
  def get(self, request):
    code = request.GET.get('code')
    url = 'https://accounts.google.com/o/oauth2/token'
    data = {
        'code': code,
        'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        'redirect_uri': request.build_absolute_uri(reverse('google-auth-callback')),
        'grant_type': 'authorization_code'
    }
    response = requests.post(url, data=data)
    token_data = response.json()

    url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    user_data = response.json()

    # check if there is SocialAccount with this email address then return the jwt token and login
    try:
      social_account = SocialAccount.objects.get(
          provider='google', uid=user_data['id'])
      user = social_account.user
      jwt_token = jwt_encode(user)
      login(request, user)
      return JsonResponse({'token': jwt_token})
    except SocialAccount.DoesNotExist:
      return JsonResponse({'error': 'This email is not associated with any account.'}, status=400)


class GoogleConnect(SocialLoginView):
  adapter_class = GoogleOAuth2Adapter
  client_class = OAuth2Client

  def connect(self, request, sociallogin):
    user = request.user
    if user.is_authenticated:
      # Connect social account to existing user account
      sociallogin.connect(request, user)
      return Response({'detail': 'Social account connected'})

    # Require authentication before connecting social account
    return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)


class GoogleSignup(SocialLoginView):
  adapter_class = GoogleOAuth2Adapter
  client_class = OAuth2Client
  permission_classes = (AllowAny,)

  def process_signup(self, request, user):
    complete_signup(request, user, self.get_adapter())
    return user


class CustomUserRegisterView(APIView):
  serializer_class = CustomUserRegisterSerializer

  def post(self, request, format=None):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      try:
        user = serializer.save()
        EmailAddress.objects.create(
            user=user, email=user.email, primary=True, verified=False)
        self.send_email_verification(request, user)
        return Response({
            "success": True,
            "code": 200,
            "detail": "Account created successfully. Please check your email for verification."
        }, status=status.HTTP_201_CREATED)
      except Exception as e:
        return Response({
            "error": True,
            "code": 400,
            "detail": "Email already exists"
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "error": True,
        "code": 400,
        "detail": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

  def send_email_verification(self, request, user):
    email_address = user.emailaddress_set.get(email=user.email)
    confirmation = EmailConfirmationHMAC(email_address)
    confirmation_key = confirmation.key
    nextjs_url = settings.NEXTJS_URL
    activate_url = f'{nextjs_url}/email/{confirmation_key}'
    context = {
        'activate_url': activate_url,
        'user': user,
        'site': settings.SITE_NAME
    }
    html_message = render_to_string(
        'account/email/email_confirmation_message.html', context)
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [user.email]
    send_mail(
        'Activate your account',
        plain_message,
        from_email,
        to,
        html_message=html_message,
    )


class CustomUserLoginView(APIView):
  serializer_class = CustomUserLoginSerializer

  def post(self, request, format=None):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        email=serializer.validated_data['email'], password=serializer.validated_data['password'])

    if not user:
      return Response({
          'error': True,
          'code': 401,
          'detail': 'Email or password incorrect'
      }, status=status.HTTP_401_UNAUTHORIZED)

    email_address = EmailAddress.objects.get(user=user, email=user.email)
    if not email_address.verified:
      return Response({
          'error': True,
          'code': 401,
          'detail': 'Email not verified'
      }, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    data = {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }

    return Response(data, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
  permission_classes = (IsAuthenticated,)

  def get(self, request):
    serializer = None
    if request.user.account_type == 'Intern':
      serializer = InternSerializer(request.user.interns)
    elif request.user.account_type == 'Recruiter':
      serializer = RecruiterSerializer(request.user.recruiters)
    else:
      raise Exception('Invalid account type')

    return Response({
        'success': True,
        'code': 200,
        'user': serializer.data
    }, status=status.HTTP_200_OK)


class CustomLogoutView(LogoutView):
  permission_classes = (IsAuthenticated,)
  authentication_classes = (JWTAuthentication,)

  def post(self, request):
    try:
      refresh_token = request.data.get('refresh')
      token = RefreshToken(refresh_token)
      token.blacklist()
      return Response(status=status.HTTP_205_RESET_CONTENT)
    except TokenError as e:
      return Response({'error': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomUserConfirmEmailView(ConfirmEmailView, APIView):
  def get(self, *args, **kwargs):
    response = super().get(*args, **kwargs)
    if response.status_code == 302:
      error_data = {
          'error': True,
          'status': status.HTTP_400_BAD_REQUEST,
          'detail': 'Email has already been confirmed'
      }
      return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    else:
      success_data = {
          'success': True,
          'status': status.HTTP_200_OK,
          'detail': 'Email has been successfully confirmed'
      }
      return Response(success_data, status=status.HTTP_200_OK)


class CustomResendEmailVerificationView(ResendEmailVerificationView):
  serializer_class = EmailVerificationSerializer

  def post(self, request, *args, **kwargs):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    if email:
      try:
        email_address = EmailAddress.objects.get(email=email).user
        if EmailAddress.objects.filter(email=email, verified=True).exists():
          return Response({
              'error': True,
              'code': 400,
              'detail': 'Email has already been verified.'
          }, status=status.HTTP_400_BAD_REQUEST)
        else:
          send_email_confirmation(request, email_address)
          return Response({
              'success': True,
              'code': 200,
              'detail': 'Email verification has been sent.'
          }, status=status.HTTP_200_OK)

      except EmailAddress.DoesNotExist:
        return Response({
            'error': True,
            'code': 400,
            'detail': 'Email does not exist.'
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
      return Response({
          'error': True,
          'code': 400,
          'detail': 'Please provide your email address.'
      }, status=status.HTTP_400_BAD_REQUEST)


class CustomPasswordChangeView(PasswordChangeView):
  permission_classes = [IsAuthenticated]


class CustomPasswordResetView(PasswordResetView):
  permission_classes = (IsAuthenticated,)

  def post(self, request, *args, **kwargs):
    email = request.data.get('email', None)
    if email:
      send_email_confirmation(request, email)
      return Response({
          'success': True,
          'code': 200,
          'detail': 'Password reset e-mail has been sent.'
      }, status=status.HTTP_200_OK)
    else:
      return Response({
          'error': True,
          'code': 400,
          'detail': 'Please provide your email address.'
      }, status=status.HTTP_400_BAD_REQUEST)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
  pass


class GoogleAuthRedirectView(View):
  def get(self, request):
    authorization_url = 'https://accounts.google.com/o/oauth2/auth'
    params = {
        'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        'redirect_uri': request.build_absolute_uri(reverse('google-auth-callback')),
        'response_type': 'code',
        'scope': 'email profile openid',
        'access_type': 'offline',
    }
    url = f'{authorization_url}?{urlencode(params)}'
    return JsonResponse({'url': url})


class GoogleAuthCallbackView(APIView):
  def get(self, request):
    code = request.GET.get('code')
    url = 'https://accounts.google.com/o/oauth2/token'
    data = {
        'code': code,
        'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        'redirect_uri': request.build_absolute_uri(reverse('google-auth-callback')),
        'grant_type': 'authorization_code'
    }
    response = requests.post(url, data=data)
    token_data = response.json()

    url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    headers = {
        'Authorization': f'Bearer {token_data["access_token"]}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    user_info = response.json()

    social_login = SocialLogin(account=None)
    adapter = DefaultSocialAccountAdapter()
    user = adapter.new_user(request=request, sociallogin=social_login)

    if SocialAccount.objects.filter(user__email=user_info.get('email', '')).exists():
      return Response({
          'error': True,
          'code': 400,
          'detail': 'User with the same email already exists.'
      }, status=status.HTTP_400_BAD_REQUEST)

    try:
      user.email = user_info.get('email', '')
      user.first_name = user_info.get('given_name', '')
      user.last_name = user_info.get('family_name', '')
      user.save()

      social_account = SocialAccount(
          user=user,
          provider='google',
          uid=user_info.get('id', ''),
          extra_data=user_info,
          socialtoken=SocialToken(
              token=token_data['access_token'],
              token_secret=token_data['refresh_token'],
              app=SocialApp.objects.get(provider='google'),
          )
      )

      social_account.save()
      send_email_confirmation(request, user, 'email_confirmation')

      return Response({
          'success': True,
          'code': 200,
          'detail': 'Account has been created. Please check your email to verify your account.',
      }, status=status.HTTP_200_OK)

    except Exception as e:
      return Response({
          'error': True,
          'code': 400,
          'detail': str(e)
      }, status=status.HTTP_400_BAD_REQUEST)

      # class GoogleAuthCreateAccountView(generics.CreateAPIView):
      #   permission_classes = [AllowAny]

      #   def post(self, request):
      #     factory = RequestFactory(content_type='application/json')
      #     serializer = self.get_serializer(data=request.data)
      #     serializer.is_valid(raise_exception=True)
      #     user = serializer.save()

      #     # Generate a temporary OAuth2 token for the new user
      #     token_url = 'https://accounts.google.com/o/oauth2/token'
      #     params = {
      #         'client_id': 'YOUR_GOOGLE_CLIENT_ID',
      #         'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',
      #         'grant_type': 'password',
      #         'username': user.email,
      #         'password': request.data.get('password'),
      #         'scope': 'email profile',
      #         'access_type': 'offline'
      #     }
      #     response = requests.post(token_url, data=params)
      #     response_json = response.json()
      #     access_token = response_json.get('access_token')

      #     # Use the access token to convert the temporary OAuth2 token to a permanent token
      #     convert_token_view = ConvertTokenView.as_view()
      #     convert_token_request = factory.post('/api/auth/convert-token/', {
      #         'grant_type': 'convert_token',
      #         'client_id': 'YOUR_GOOGLE_CLIENT_ID',
      #         'client_secret': 'YOUR_GOOGLE_CLIENT_SECRET',
      #         'backend': 'google-oauth2',
      #         'token': access_token
      #     })
      #     convert_token_response = convert_token_view(convert_token_request)

      #     # Log in the user using the permanent OAuth2 token
      #     login(request, convert_token_response.user)

      #     # Redirect the user to the desired page
