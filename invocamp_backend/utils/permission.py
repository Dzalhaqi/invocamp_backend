from rest_framework import permissions
from vacancies.models import Recruiter, Intern


class IsRecruiter(permissions.BasePermission):
  def has_permission(self, request, view):
    return Recruiter.objects.filter(user_profile=request.user).exists()


class IsIntern(permissions.BasePermission):
  def has_permission(self, request, view):
    return Intern.objects.filter(user_profile=request.user).exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
  def has_object_permission(self, request, view, obj):
    return obj.applicant == request.user or request.method in permissions.SAFE_METHODS
