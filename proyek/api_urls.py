# Import router bawaan dari Django REST Framework
from rest_framework.routers import DefaultRouter

# Import ViewSet untuk Project dari views.py
from .views import ProjectViewSet

# Membuat router default (otomatis menangani routing REST API)
router = DefaultRouter()

# Mendaftarkan rute 'proyek' ke dalam router, mengarah ke ProjectViewSet
# basename='proyek' menentukan nama dasar untuk URL pattern yang dihasilkan
router.register(r'proyek', ProjectViewSet, basename='proyek')

# Menghasilkan daftar URL dari router untuk digunakan dalam urlpatterns
urlpatterns = router.urls
