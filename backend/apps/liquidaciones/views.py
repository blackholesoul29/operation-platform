from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import Liquidacion, CostoOperativo
from .serializers import LiquidacionSerializer, LiquidacionListSerializer, CostoOperativoSerializer


class LiquidacionViewSet(viewsets.ModelViewSet):
    queryset = Liquidacion.objects.all().order_by('-periodo_anio', '-periodo_mes')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cliente', 'planta', 'servicio', 'estado', 'periodo_mes', 'periodo_anio']
    search_fields = ['observaciones']
    ordering_fields = ['periodo_anio', 'periodo_mes', 'estado']

    def get_serializer_class(self):
        if self.action == 'list':
            return LiquidacionListSerializer
        return LiquidacionSerializer


class CostoOperativoViewSet(viewsets.ModelViewSet):
    queryset = CostoOperativo.objects.all().order_by('-fecha')
    serializer_class = CostoOperativoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo', 'planta', 'periodo_mes', 'periodo_anio']
    ordering_fields = ['fecha', 'valor_cop']
