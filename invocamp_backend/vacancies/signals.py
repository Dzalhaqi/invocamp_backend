from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import VacancyPost, VacancyApplication


@receiver(post_delete, sender=VacancyApplication)
def remove_applicant_from_vacancy_post(sender, instance, **kwargs):
  vacancy_post = instance.vacancy
  applicant = instance.applicant

  if vacancy_post.applicants.filter(user_profile=applicant.user_profile).exists():
    vacancy_post.applicants.remove(applicant)
