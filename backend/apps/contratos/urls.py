from rest_framework.routers import DefaultRouter

from .views import IndiceIPPViewSet, IndiceIPCViewSet, ContratoPPAViewSet, GesconAsignacionViewSet

router = DefaultRouter()
router.register(r'ipp', IndiceIPPViewSet, basename='ipp')
router.register(r'ipc', IndiceIPCViewSet, basename='ipc')
router.register(r'ppa', ContratoPPAViewSet, basename='ppa')
router.register(r'gescon', GesconAsignacionViewSet, basename='gescon')

urlpatterns = router.urls
