from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Servicio, Planta, ClientePlanta, ClienteServicio, Frontera
from .serializers import (
    ServicioSerializer,
    PlantaSerializer,
    PlantaListSerializer,
    FronteraSerializer,
    ClientePlantaSerializer,
    ClienteServicioSerializer,
)


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer


class PlantaViewSet(viewsets.ModelViewSet):
    queryset = Planta.objects.all().order_by('nombre')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'tecnologia', 'departamento']
    search_fields = ['nombre', 'codigo_sic']
    ordering_fields = ['nombre', 'potencia_efectiva_kw', 'fecha_inicio_operacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return PlantaListSerializer
        return PlantaSerializer


class FronteraViewSet(viewsets.ModelViewSet):
    queryset = Frontera.objects.all()
    serializer_class = FronteraSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['planta', 'tipo']


class ClientePlantaViewSet(viewsets.ModelViewSet):
    queryset = ClientePlanta.objects.all()
    serializer_class = ClientePlantaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cliente', 'planta', 'es_inversionista']


class ClienteServicioViewSet(viewsets.ModelViewSet):
    queryset = ClienteServicio.objects.all()
    serializer_class = ClienteServicioSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cliente', 'planta', 'servicio', 'estado']
