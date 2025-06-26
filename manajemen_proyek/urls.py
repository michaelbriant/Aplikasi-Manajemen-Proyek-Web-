from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from proyek import views  # Impor views utama dari aplikasi proyek

# -----------------------------------------
# Daftar URL utama aplikasi Django
# -----------------------------------------
urlpatterns = [
    # URL untuk halaman admin Django
    path('admin/', admin.site.urls),

    # URL untuk halaman landing page utama (root "/")
    path('', views.landing_page, name='landing'),

    # URL untuk login pengguna
    path('login/', views.login_view, name='login'),

    # URL ke semua endpoint dalam aplikasi proyek (menggunakan include)
    path('homepage', include('proyek.urls')),

    # URL untuk API (REST API endpoint dari proyek)
    path('api/', include('proyek.api_urls')), 
]

# -----------------------------------------
# Saat mode DEBUG aktif, izinkan akses file media langsung dari URL
# (biasanya hanya untuk pengembangan)
# -----------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
