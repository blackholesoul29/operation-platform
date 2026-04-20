from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Cliente, Contacto
from .serializers import ClienteSerializer, ClienteListSerializer, ContactoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('-creado_en')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'etapa', 'ciudad', 'departamento']
    search_fields = ['razon_social', 'nit', 'email']
    ordering_fields = ['razon_social', 'creado_en', 'etapa']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        return ClienteSerializer


class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.all().order_by('nombre_completo')
    serializer_class = ContactoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['cliente', 'es_decisor']
    search_fields = ['nombre_completo', 'email', 'cargo']
