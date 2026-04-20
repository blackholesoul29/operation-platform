from rest_framework.routers import DefaultRouter

from .views import ReporteFronteraViewSet, BalanceEnergeticoViewSet

router = DefaultRouter()
router.register(r'reportes', ReporteFronteraViewSet, basename='reporte-frontera')
router.register(r'balance', BalanceEnergeticoViewSet, basename='balance')

urlpatterns = router.urls
