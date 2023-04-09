from django.contrib import admin
from .models import VacancyApplication, VacancyPost
# Register your models here.

# register the models
admin.site.register(VacancyPost)
admin.site.register(VacancyApplication)
