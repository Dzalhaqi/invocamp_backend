from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from .views import protected_serve

admin.site.site_header = "InvoCamp Site | Header"
admin.site.site_title = "InvoCamp Title"
admin.site.index_title = "Welcome to InvoCamp Admin"

urlpatterns = [
    re_path(r'^{}(?P<path>.*)$'.format(settings.MEDIA_URL[1:]),
            protected_serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('api/', include('account_app.urls')),
    path('api/', include('vacancies.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('', RedirectView.as_view(url='api/')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
  import debug_toolbar

  urlpatterns = [
      path('__debug__/', include(debug_toolbar.urls)),
  ] + urlpatterns

  urlpatterns += static(settings.MEDIA_URL,
                        document_root=settings.MEDIA_ROOT)

handler404 = 'invocamp_backend.views.handler_404'
handler500 = 'invocamp_backend.views.handler_500'
