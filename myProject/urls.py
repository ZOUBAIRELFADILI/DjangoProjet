
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from GrapheApp import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('GrapheApp.urls')), 
]

if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
