from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title = "Habr Clone API",
      default_version = 'v1',
      description = "Here you can read doc about our API",
      contact = openapi.Contact(email = "aren.allahverdyan@gmail.com"),
   ),
   public = True,
   permission_classes = (permissions.AllowAny,),
)

urlpatterns = [
   path('admin/', admin.site.urls),
   path('users/', include('users.urls', namespace = 'users')),
   path('publications/', include('publications.urls', namespace = 'publications')),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout = 0), name = 'schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout = 0), name = 'schema-redoc'),
]

if settings.DEBUG:
   import debug_toolbar
   urlpatterns += [
      path('__debug__/', include(debug_toolbar.urls)),
   ] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
   