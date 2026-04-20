from rest_framework.routers import DefaultRouter

from .views import LiquidacionViewSet, CostoOperativoViewSet

router = DefaultRouter()
router.register(r'costos', CostoOperativoViewSet, basename='costo')
router.register(r'', LiquidacionViewSet, basename='liquidacion')

urlpatterns = router.urls
