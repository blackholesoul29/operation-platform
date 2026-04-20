from rest_framework.routers import DefaultRouter

from .views import (
    PlantaViewSet,
    FronteraViewSet,
    ClientePlantaViewSet,
    ClienteServicioViewSet,
    ServicioViewSet,
)

router = DefaultRouter()
router.register(r'plantas', PlantaViewSet, basename='planta')
router.register(r'fronteras', FronteraViewSet, basename='frontera')
router.register(r'participaciones', ClientePlantaViewSet, basename='clienteplanta')
router.register(r'servicios-contratados', ClienteServicioViewSet, basename='clienteservicio')
router.register(r'servicios', ServicioViewSet, basename='servicio')

urlpatterns = router.urls
