from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, ContactoViewSet

router = DefaultRouter()
router.register(r'', ClienteViewSet, basename='cliente')
router.register(r'contactos', ContactoViewSet, basename='contacto')

urlpatterns = router.urls
