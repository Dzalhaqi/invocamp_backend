from account_app.models import Recruiter, Intern


def is_recruiter(user):
  return Recruiter.objects.filter(user_profile=user).exists()

def is_intern(user):
  return Intern.objects.filter(user_profile=user).exists()
