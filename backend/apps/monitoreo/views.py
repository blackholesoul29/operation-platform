from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Falla, DatoGeneracion
from .serializers import FallaSerializer, DatoGeneracionSerializer


class FallaViewSet(viewsets.ModelViewSet):
    queryset = Falla.objects.all().order_by('-fecha_deteccion')
    serializer_class = FallaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['planta', 'criticidad', 'estado', 'categoria']
    search_fields = ['descripcion', 'codigo_falla', 'centinela']
    ordering_fields = ['fecha_deteccion']

    @action(detail=False, methods=['get'], url_path='resumen')
    def resumen(self, request):
        """Totales y distribución de fallas por criticidad y estado."""
        data = {
            'total': Falla.objects.count(),
            'abiertas': Falla.objects.filter(estado='ABIERTA').count(),
            'criticas': Falla.objects.filter(
                criticidad='CRITICA',
                estado__in=['ABIERTA', 'EN_PROGRESO'],
            ).count(),
            'por_criticidad': list(
                Falla.objects.values('criticidad').annotate(total=Count('id'))
            ),
            'por_estado': list(
                Falla.objects.values('estado').annotate(total=Count('id'))
            ),
        }
        return Response(data)


class DatoGeneracionViewSet(viewsets.ModelViewSet):
    queryset = DatoGeneracion.objects.all().order_by('-fecha')
    serializer_class = DatoGeneracionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['planta', 'fuente', 'validado', 'fecha']
    ordering_fields = ['fecha']
