import calendar
from datetime import datetime

from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import ReporteFrontera, BalanceEnergetico
from .serializers import ReporteFronteraSerializer, BalanceEnergeticoSerializer


class ReporteFronteraViewSet(viewsets.ModelViewSet):
    queryset = ReporteFrontera.objects.all().order_by('-fecha_reporte')
    serializer_class = ReporteFronteraSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['planta', 'estado', 'fecha_reporte']
    ordering_fields = ['fecha_reporte']

    @action(detail=False, methods=['get'], url_path='completitud')
    def completitud(self, request):
        """Porcentaje de reportes subidos por planta en un periodo."""
        anio = int(request.query_params.get('anio', datetime.now().year))
        mes = int(request.query_params.get('mes', datetime.now().month))
        dias_mes = calendar.monthrange(anio, mes)[1]

        from apps.proyectos.models import Planta
        resultado = []
        for planta in Planta.objects.filter(estado='OPERANDO'):
            subidos = ReporteFrontera.objects.filter(
                planta=planta,
                fecha_reporte__year=anio,
                fecha_reporte__month=mes,
                estado__in=['SUBIDO', 'VALIDADO'],
            ).count()
            resultado.append({
                'planta_id': planta.id,
                'planta_nombre': planta.nombre,
                'dias_mes': dias_mes,
                'reportes_subidos': subidos,
                'completitud_pct': round(subidos / dias_mes * 100, 1),
            })
        return Response(resultado)


class BalanceEnergeticoViewSet(viewsets.ModelViewSet):
    queryset = BalanceEnergetico.objects.all().order_by('-periodo_anio', '-periodo_mes')
    serializer_class = BalanceEnergeticoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['planta', 'periodo_anio', 'periodo_mes', 'fuente', 'validado']
    ordering_fields = ['periodo_anio', 'periodo_mes']
