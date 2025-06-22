from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from proyek import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('homepage', include('proyek.urls')),
    path('api/', include('proyek.api_urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
