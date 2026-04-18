from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task(name='apps.notificaciones.tasks.check_document_expiry')
def check_document_expiry():
    """Find documents expiring within 15 days and create notifications."""
    from apps.documentos.models import Documento
    from apps.notificaciones.models import Notificacion

    today = timezone.now().date()
    threshold = today + timedelta(days=15)

    expiring = Documento.objects.filter(
        fecha_vencimiento__lte=threshold,
        fecha_vencimiento__gte=today,
        estado__in=['recibido', 'aprobado']
    ).select_related('cliente', 'deal__comercial', 'tipo_documento')

    created = 0
    for doc in expiring:
        days_left = (doc.fecha_vencimiento - today).days
        user = None
        if doc.deal and doc.deal.comercial:
            user = doc.deal.comercial
        elif doc.cliente and doc.cliente.comercial_asignado:
            user = doc.cliente.comercial_asignado

        if not user:
            continue

        # Avoid duplicate notifications today
        existing = Notificacion.objects.filter(
            usuario=user,
            documento=doc,
            tipo='documento_por_vencer',
            created_at__date=today
        ).exists()

        if not existing:
            doc_name = doc.tipo_documento.nombre if doc.tipo_documento else doc.nombre
            cliente_name = doc.cliente.nombre if doc.cliente else 'N/A'
            Notificacion.objects.create(
                usuario=user,
                tipo='documento_por_vencer',
                titulo=f"Documento por vencer: {doc_name}",
                mensaje=(
                    f"El documento '{doc_name}' del cliente {cliente_name} "
                    f"vence en {days_left} días ({doc.fecha_vencimiento})."
                ),
                deal=doc.deal,
                cliente=doc.cliente,
                documento=doc,
            )
            created += 1

    return f"Created {created} expiry notifications"


@shared_task(name='apps.notificaciones.tasks.check_deal_stagnation')
def check_deal_stagnation():
    """Find active deals with no activity for more than 7 days."""
    from apps.deals.models import Deal, ETAPAS_ACTIVAS
    from apps.notificaciones.models import Notificacion

    threshold = timezone.now() - timedelta(days=7)
    stagnant_deals = Deal.objects.filter(
        etapa__in=ETAPAS_ACTIVAS,
        updated_at__lt=threshold,
        comercial__isnull=False
    ).select_related('comercial', 'cliente')

    created = 0
    for deal in stagnant_deals:
        existing = Notificacion.objects.filter(
            deal=deal,
            tipo='deal_estancado',
            created_at__date=timezone.now().date()
        ).exists()
        if not existing:
            Notificacion.objects.create(
                usuario=deal.comercial,
                tipo='deal_estancado',
                titulo=f"Deal sin actividad: {deal.nombre}",
                mensaje=(
                    f"El deal '{deal.nombre}' con {deal.cliente.nombre} "
                    f"lleva más de 7 días sin actividad en etapa '{deal.get_etapa_display()}'."
                ),
                deal=deal,
                cliente=deal.cliente,
            )
            created += 1

    return f"Created {created} stagnation notifications"


@shared_task(name='apps.notificaciones.tasks.check_contract_unsigned')
def check_contract_unsigned():
    """Find deals in 'contrato' stage for more than 5 days."""
    from apps.deals.models import Deal
    from apps.notificaciones.models import Notificacion

    threshold = timezone.now() - timedelta(days=5)
    unsigned = Deal.objects.filter(
        etapa='contrato',
        etapa_changed_at__lt=threshold,
        comercial__isnull=False
    ).select_related('comercial', 'cliente')

    created = 0
    for deal in unsigned:
        existing = Notificacion.objects.filter(
            deal=deal,
            tipo='contrato_sin_firma',
            created_at__date=timezone.now().date()
        ).exists()
        if not existing:
            Notificacion.objects.create(
                usuario=deal.comercial,
                tipo='contrato_sin_firma',
                titulo=f"Contrato pendiente de firma: {deal.nombre}",
                mensaje=(
                    f"El contrato del deal '{deal.nombre}' con {deal.cliente.nombre} "
                    f"lleva más de 5 días pendiente de firma."
                ),
                deal=deal,
                cliente=deal.cliente,
            )
            created += 1

    return f"Created {created} unsigned contract notifications"


@shared_task(name='apps.notificaciones.tasks.check_pending_tasks')
def check_pending_tasks():
    """Find overdue tasks and notify assigned users."""
    from apps.tareas.models import Tarea
    from apps.notificaciones.models import Notificacion

    overdue = Tarea.objects.filter(
        completada=False,
        fecha_limite__lt=timezone.now(),
        asignado_a__isnull=False
    ).select_related('asignado_a', 'deal', 'cliente')

    created = 0
    for tarea in overdue:
        existing = Notificacion.objects.filter(
            usuario=tarea.asignado_a,
            tipo='tarea_vencida',
            created_at__date=timezone.now().date(),
            deal=tarea.deal,
        ).filter(titulo__contains=tarea.titulo[:50]).exists()

        if not existing:
            Notificacion.objects.create(
                usuario=tarea.asignado_a,
                tipo='tarea_vencida',
                titulo=f"Tarea vencida: {tarea.titulo[:80]}",
                mensaje=(
                    f"La tarea '{tarea.titulo}' venció el "
                    f"{tarea.fecha_limite.strftime('%d/%m/%Y')}."
                ),
                deal=tarea.deal,
                cliente=tarea.cliente,
            )
            created += 1

    return f"Created {created} overdue task notifications"
