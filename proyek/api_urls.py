from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register(r'proyek', ProjectViewSet, basename='proyek')

urlpatterns = router.urls
