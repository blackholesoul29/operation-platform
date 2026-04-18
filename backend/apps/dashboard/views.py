from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.deals.models import Deal, DealServicio, ETAPAS_ACTIVAS, ETAPAS_CERRADAS
from apps.deals.serializers import DealListSerializer
from apps.tareas.models import Tarea
from apps.notificaciones.models import Notificacion
from apps.clientes.models import Cliente
from apps.users.permissions import get_user_role, ROLE_HIERARCHY


def _get_deals_queryset(user):
    """Return role-filtered deals queryset."""
    role = get_user_role(user)
    qs = Deal.objects.select_related('cliente', 'comercial', 'comercial__profile').prefetch_related('deal_servicios')
    if ROLE_HIERARCHY.get(role, 0) < 3:
        qs = qs.filter(comercial=user)
    return qs


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = get_user_role(user)
        is_manager_plus = ROLE_HIERARCHY.get(role, 0) >= 3

        deals_qs = _get_deals_queryset(user)

        # Deals activos
        deals_activos = deals_qs.filter(etapa__in=ETAPAS_ACTIVAS).count()

        # Deals cerrados este mes
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        deals_cerrados_ganados_mes = deals_qs.filter(
            etapa='cerrado_ganado',
            updated_at__gte=month_start
        ).count()

        deals_cerrados_perdidos_mes = deals_qs.filter(
            etapa='cerrado_perdido',
            updated_at__gte=month_start
        ).count()

        # Valor total del pipeline
        valor_result = deals_qs.filter(
            etapa__in=ETAPAS_ACTIVAS
        ).aggregate(total=Sum('valor_estimado'))
        valor_pipeline_total = str(valor_result['total'] or 0)

        # Tasa de conversión
        total_cerrados = deals_qs.filter(etapa__in=ETAPAS_CERRADAS).count()
        ganados = deals_qs.filter(etapa='cerrado_ganado').count()
        tasa_conversion = round((ganados / total_cerrados * 100), 1) if total_cerrados > 0 else 0.0

        # Deals por etapa
        all_etapas = [e[0] for e in Deal.ETAPAS]
        deals_por_etapa = {}
        for etapa in all_etapas:
            deals_por_etapa[etapa] = deals_qs.filter(etapa=etapa).count()

        # Deals por tipo de servicio
        servicios_all = ['representacion', 'cgm', 'monitoreo', 'ppa', 'venta_energia', 'recs']
        deals_por_tipo_servicio = {}
        for servicio in servicios_all:
            if is_manager_plus:
                count = DealServicio.objects.filter(servicio=servicio).count()
            else:
                count = DealServicio.objects.filter(
                    servicio=servicio,
                    deal__comercial=user
                ).count()
            deals_por_tipo_servicio[servicio] = count

        # Mis tareas
        tareas_qs = Tarea.objects.filter(
            Q(asignado_a=user) | Q(creado_por=user)
        )
        mis_tareas_pendientes = tareas_qs.filter(completada=False).count()
        mis_tareas_vencidas = tareas_qs.filter(
            completada=False,
            fecha_limite__lt=now
        ).count()

        # Notificaciones no leídas
        notificaciones_no_leidas = Notificacion.objects.filter(
            usuario=user, leida=False
        ).count()

        # Clientes activos
        if is_manager_plus:
            clientes_activos = Cliente.objects.filter(activo=True).count()
        else:
            clientes_activos = Cliente.objects.filter(
                activo=True, comercial_asignado=user
            ).count()

        return Response({
            'deals_activos': deals_activos,
            'deals_cerrados_ganados_mes': deals_cerrados_ganados_mes,
            'deals_cerrados_perdidos_mes': deals_cerrados_perdidos_mes,
            'valor_pipeline_total': valor_pipeline_total,
            'tasa_conversion': tasa_conversion,
            'deals_por_etapa': deals_por_etapa,
            'deals_por_tipo_servicio': deals_por_tipo_servicio,
            'mis_tareas_pendientes': mis_tareas_pendientes,
            'mis_tareas_vencidas': mis_tareas_vencidas,
            'notificaciones_no_leidas': notificaciones_no_leidas,
            'clientes_activos': clientes_activos,
        })


class PipelineSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deals_qs = _get_deals_queryset(request.user).filter(
            etapa__in=ETAPAS_ACTIVAS
        ).prefetch_related('deal_servicios', 'tareas', 'documentos', 'actividades')

        etapas_order = ['prospeccion', 'primer_contacto', 'oferta_enviada', 'negociacion', 'contrato']
        pipeline = {etapa: [] for etapa in etapas_order}

        for deal in deals_qs:
            if deal.etapa in pipeline:
                pipeline[deal.etapa].append(
                    DealListSerializer(deal, context={'request': request}).data
                )

        return Response(pipeline)
