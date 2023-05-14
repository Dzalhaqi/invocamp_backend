from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from account_app.views.account_views import (CurrentUserView, CustomUserConfirmEmailView, CustomResendEmailVerificationView, CustomUserRegisterView, GoogleLogin, GoogleLoginView, CustomUserLoginView,
                                             GoogleConnect, GoogleSignup, CustomLogoutView, CustomPasswordChangeView, CustomPasswordResetView, CustomPasswordResetConfirmView, GoogleAuthCallbackView, GoogleAuthRedirectView)
from dj_rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView, VerifyEmailView
)

from account_app.views.intern_view import InternUpdateView
from account_app.views.recruiter_view import RecruiterUpdateView

router = DefaultRouter()

urlpatterns = [
    # account urls
    path('', include(router.urls)),
    # path('allauth/', include('allauth.urls')),
    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/google/login/', GoogleLogin().as_view(), name='google_login'),
    # path('auth/google/connect/', GoogleConnect.as_view(), name='google_connect'),
    path('auth/register/', CustomUserRegisterView.as_view(), name='account_signup'),
    path('auth/login/', CustomUserLoginView.as_view(), name='account_login'),
    path('auth/me/', CurrentUserView().as_view(), name='account_user'),
    path('auth/confirm-email/<str:key>/', CustomUserConfirmEmailView.as_view(),
         name='account_confirm_email'),
    path('auth/resend-verification-email/', CustomResendEmailVerificationView.as_view(),
         name='account_resend_verification_email'),
    # path('auth/password/change/', CustomPasswordChangeView.as_view(),
    #      name='rest_password_change'),
    # path('auth/password/reset/', CustomPasswordResetView.as_view(),
    #      name='rest_password_reset'),
    # path('auth/password/reset/confirm/<str:uidb64>/<str:token>/',
    #      CustomPasswordResetConfirmView.as_view(), name='rest_password_reset_confirm'),
    path('auth/google/', GoogleAuthRedirectView.as_view(), name='google-auth'),
    path('auth/google/callback', GoogleAuthCallbackView.as_view(),
         name='google-auth-callback'),
    path(
        'socialaccounts/',
        SocialAccountListView.as_view(),
        name='social_account_list'
    ),
    path(
        'socialaccounts/<int:pk>/disconnect/',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'
    ),

    # intern urls
    path('intern/<int:user_profile>/',
         InternUpdateView.as_view(), name='intern-profile'),

    # recruiter urls
    path('recruiter/<int:user_profile>/',
         RecruiterUpdateView.as_view(), name='recruiter-profile'),
]
