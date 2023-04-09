from django.contrib import admin
from django.http import HttpResponse


class CustomAdminSite(admin.sites.AdminSite):
  site_header = "InvoCamp Site | Header"
  site_title = "InvoCamp Title"
  index_title = "Welcome to InvoCamp Admin"

  class Media:
    css = {
        'all': ('admin/css/custom.css',)
    }


admin_site = CustomAdminSite(name='custom_admin')
