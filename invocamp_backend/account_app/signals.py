from django.db.models.signals import post_save
from django.dispatch import receiver
# from .models import CustomUser
from django.apps import apps


@receiver(post_save, sender=apps.get_model('account_app', 'CustomUser'))
def create_account_profile(sender, instance, created, **kwargs):
  if created:
    if instance.account_type == 'RECRUITER':
      recruiter_model = apps.get_model('account_app', 'Recruiter')
      recruiter_model.objects.create(user_profile=instance)
    elif instance.account_type == 'INTERN':
      intern_model = apps.get_model('account_app', 'Intern')
      intern_model.objects.create(user_profile=instance)
