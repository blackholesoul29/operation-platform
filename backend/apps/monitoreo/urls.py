from rest_framework.routers import DefaultRouter

from .views import FallaViewSet, DatoGeneracionViewSet

router = DefaultRouter()
router.register(r'fallas', FallaViewSet, basename='falla')
router.register(r'generacion', DatoGeneracionViewSet, basename='generacion')

urlpatterns = router.urls
