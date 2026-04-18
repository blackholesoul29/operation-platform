from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cliente, Contacto
from .serializers import (
    ClienteCreateUpdateSerializer,
    ClienteDetailSerializer,
    ClienteListSerializer,
    ContactoSerializer,
)


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['segmento', 'comercial_asignado', 'activo']
    search_fields = ['nombre', 'nit', 'ciudad']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    def get_queryset(self):
        return Cliente.objects.select_related(
            'comercial_asignado',
            'comercial_asignado__profile'
        ).prefetch_related('contactos').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ClienteCreateUpdateSerializer
        return ClienteListSerializer

    def create(self, request, *args, **kwargs):
        serializer = ClienteCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            return Response(ClienteDetailSerializer(cliente).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = ClienteCreateUpdateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            cliente = serializer.save()
            return Response(ClienteDetailSerializer(cliente).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='deals')
    def deals(self, request, pk=None):
        from apps.deals.serializers import DealListSerializer
        cliente = self.get_object()
        qs = cliente.deals.select_related(
            'comercial', 'comercial__profile', 'cliente'
        ).prefetch_related('deal_servicios').all()
        serializer = DealListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='contactos')
    def add_contacto(self, request, pk=None):
        cliente = self.get_object()
        data = request.data.copy()
        data['cliente'] = cliente.id
        serializer = ContactoSerializer(data=data)
        if serializer.is_valid():
            serializer.save(cliente=cliente)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
