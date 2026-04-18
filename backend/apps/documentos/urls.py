from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DocumentoViewSet, TipoDocumentoViewSet

router = DefaultRouter()
router.register(r'tipos', TipoDocumentoViewSet, basename='tipo-documento')
router.register(r'', DocumentoViewSet, basename='documento')

urlpatterns = [
    path('', include(router.urls)),
]
