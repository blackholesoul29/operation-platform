from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Documento
from .serializers import DocumentoSerializer, DocumentoListSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all().order_by('-subido_en')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'cliente', 'planta', 'frontera', 'liquidacion']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['subido_en', 'nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentoListSerializer
        return DocumentoSerializer
