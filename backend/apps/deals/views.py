from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Deal, ActividadDeal, ETAPAS_ACTIVAS, ETAPAS_CERRADAS
from .serializers import (
    DealListSerializer,
    DealDetailSerializer,
    DealCreateUpdateSerializer,
    CambiarEtapaSerializer,
    ActividadDealSerializer,
)
from apps.users.permissions import get_user_role, ROLE_HIERARCHY


def _create_auto_task(deal, titulo, dias, creado_por):
    """Helper to create an auto-generated task for a deal."""
    from apps.tareas.models import Tarea
    fecha_limite = timezone.now() + timedelta(days=dias)
    Tarea.objects.create(
        titulo=titulo,
        deal=deal,
        cliente=deal.cliente,
        asignado_a=deal.comercial,
        creado_por=creado_por,
        fecha_limite=fecha_limite,
        prioridad='alta',
        auto_generada=True,
    )


AUTO_TASKS = {
    'primer_contacto': [
        ('Enviar NDA y solicitar documentos iniciales (RUT, CERL)', 2),
    ],
    'oferta_enviada': [
        ('Hacer seguimiento a la oferta en 5 días hábiles', 5),
    ],
    'negociacion': [
        ('Solicitar documentación completa según servicios contratados', 3),
    ],
    'contrato': [
        ('Revisión legal interna del contrato', 5),
        ('Enviar contrato al cliente', 7),
    ],
    'cerrado_ganado': [
        ('Coordinar handoff al equipo operativo', 3),
    ],
}


class DealViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['etapa', 'tipo_pipeline', 'comercial', 'cliente']
    search_fields = ['nombre', 'cliente__nombre', 'cliente__nit']
    ordering_fields = ['created_at', 'nombre', 'valor_estimado', 'fecha_estimada_cierre']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        role = get_user_role(user)
        qs = Deal.objects.select_related(
            'cliente', 'comercial', 'comercial__profile'
        ).prefetch_related('deal_servicios', 'tareas', 'documentos', 'actividades')

        # Role-based filtering
        if ROLE_HIERARCHY.get(role, 0) < 3:
            qs = qs.filter(comercial=user)

        # Filter by is_cerrado query param
        is_cerrado = self.request.query_params.get('is_cerrado')
        if is_cerrado is not None:
            if is_cerrado.lower() in ('true', '1'):
                qs = qs.filter(etapa__in=ETAPAS_CERRADAS)
            else:
                qs = qs.filter(etapa__in=ETAPAS_ACTIVAS)

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DealDetailSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return DealCreateUpdateSerializer
        return DealListSerializer

    def create(self, request, *args, **kwargs):
        serializer = DealCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            deal = serializer.save()
            return Response(DealDetailSerializer(deal).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = DealCreateUpdateSerializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            deal = serializer.save()
            return Response(DealDetailSerializer(deal).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='cambiar-etapa')
    def cambiar_etapa(self, request, pk=None):
        deal = self.get_object()
        serializer = CambiarEtapaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        etapa_nueva = serializer.validated_data['etapa_nueva']
        motivo = serializer.validated_data.get('motivo', '')
        descripcion_actividad = serializer.validated_data.get('descripcion_actividad', '')

        etapa_anterior = deal.etapa
        etapa_anterior_display = deal.get_etapa_display()

        deal.etapa = etapa_nueva
        deal.etapa_changed_at = timezone.now()
        if motivo:
            deal.motivo_cierre = motivo
        deal.save()

        # Build activity description
        etapa_nueva_display = dict(Deal.ETAPAS).get(etapa_nueva, etapa_nueva)
        desc = f"Etapa cambiada de '{etapa_anterior_display}' a '{etapa_nueva_display}'."
        if motivo:
            desc += f" Motivo: {motivo}"
        if descripcion_actividad:
            desc += f" {descripcion_actividad}"

        ActividadDeal.objects.create(
            deal=deal,
            tipo='cambio_etapa',
            descripcion=desc,
            creado_por=request.user,
        )

        # Auto-create tasks based on new stage
        tasks_to_create = AUTO_TASKS.get(etapa_nueva, [])
        for titulo, dias in tasks_to_create:
            _create_auto_task(deal, titulo, dias, request.user)

        return Response(DealDetailSerializer(deal).data)

    @action(detail=True, methods=['get', 'post'], url_path='actividades')
    def actividades(self, request, pk=None):
        deal = self.get_object()
        if request.method == 'GET':
            qs = deal.actividades.all()
            serializer = ActividadDealSerializer(qs, many=True)
            return Response(serializer.data)
        else:
            data = request.data.copy()
            serializer = ActividadDealSerializer(data=data)
            if serializer.is_valid():
                ActividadDeal.objects.create(
                    deal=deal,
                    tipo=serializer.validated_data['tipo'],
                    descripcion=serializer.validated_data['descripcion'],
                    creado_por=request.user,
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='checklist')
    def checklist(self, request, pk=None):
        from apps.documentos.models import DocumentoRequerido, Documento

        deal = self.get_object()
        servicios = list(deal.deal_servicios.values_list('servicio', flat=True))

        requeridos = DocumentoRequerido.objects.filter(
            servicio__in=servicios
        ).select_related('tipo_documento').distinct()

        result = []
        for req in requeridos:
            doc = Documento.objects.filter(
                deal=deal,
                tipo_documento=req.tipo_documento
            ).order_by('-version').first()

            result.append({
                'tipo_documento': req.tipo_documento.codigo,
                'nombre': req.tipo_documento.nombre,
                'obligatorio': req.obligatorio,
                'estado': doc.estado if doc else 'pendiente',
                'documento_id': doc.id if doc else None,
            })

        return Response(result)
