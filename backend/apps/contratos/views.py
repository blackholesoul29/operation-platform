from rest_framework import viewsets, filters

from django_filters.rest_framework import DjangoFilterBackend

from .models import IndiceIPP, IndiceIPC, ContratoPPA, GesconAsignacion
from .serializers import (
    IndiceIPPSerializer,
    IndiceIPCSerializer,
    ContratoPPASerializer,
    GesconAsignacionSerializer,
)


class IndiceIPPViewSet(viewsets.ModelViewSet):
    queryset = IndiceIPP.objects.all().order_by('-anio', '-mes')
    serializer_class = IndiceIPPSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['anio', 'mes', 'es_provisional']
    ordering_fields = ['anio', 'mes']


class IndiceIPCViewSet(viewsets.ModelViewSet):
    queryset = IndiceIPC.objects.all().order_by('-anio')
    serializer_class = IndiceIPCSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['anio']


class ContratoPPAViewSet(viewsets.ModelViewSet):
    queryset = ContratoPPA.objects.all()
    serializer_class = ContratoPPASerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['cliente', 'planta', 'tipo', 'estado', 'modalidad']
    search_fields = ['codigo_contrato']


class GesconAsignacionViewSet(viewsets.ModelViewSet):
    queryset = GesconAsignacion.objects.all().order_by('-periodo_anio', '-periodo_mes')
    serializer_class = GesconAsignacionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['planta', 'tipo', 'periodo_anio', 'periodo_mes']
    ordering_fields = ['periodo_anio', 'periodo_mes']
