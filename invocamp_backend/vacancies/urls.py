from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (VacancyPostViewSet, VacancyPostedListAPIView, VacancyApplicationInternViewSet,
                    VacancyPostedRetrieveAPIView, VacancyPostedApplicationsListAPIView,
                    VacancyPostedApplicationsRetrieveAPIView, VacancyPostedApplicationsUpdateAPIView, VacancyPostedApplicationsRetrieveUpdateAPIView)

router = DefaultRouter()
router.register(r'vacancies', VacancyPostViewSet, basename='vacancies')
router.register(r'vacancies-applications',
                VacancyApplicationInternViewSet, basename='vacancies-applications')

urlpatterns = [
    path('', include(router.urls)),
    path('vacancies-posted/',
         VacancyPostedListAPIView.as_view(), name='vacancies-posted-list'),
    path('vacancies-posted/<int:vacancy_id>/',
         VacancyPostedRetrieveAPIView.as_view(), name='vacancies-posted-detail'),
    path('vacancies-posted/<int:vacancy_id>/applications/',
         VacancyPostedApplicationsListAPIView().as_view(), name='vacancies-applications-list'),
    path('vacancies-posted/<int:vacancy_id>/applications/<int:application_id>/',
         VacancyPostedApplicationsRetrieveUpdateAPIView.as_view(), name='vacancies-applications-detail-update'),
]
