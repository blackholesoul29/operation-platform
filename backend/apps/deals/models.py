from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

SERVICIOS_CHOICES = [
    ('representacion', 'Representación de Frontera'),
    ('cgm', 'CGM'),
    ('monitoreo', 'Monitoreo'),
    ('ppa', 'PPA'),
    ('venta_energia', 'Venta de Energía'),
    ('recs', 'RECs'),
]

ETAPAS_ACTIVAS = ['prospeccion', 'primer_contacto', 'oferta_enviada', 'negociacion', 'contrato']
ETAPAS_CERRADAS = ['cerrado_ganado', 'cerrado_perdido', 'sin_interes']


class Deal(models.Model):
    TIPO_PIPELINE = [
        ('servicios_principales', 'Servicios Principales'),
        ('recs', 'RECs'),
    ]
    ETAPAS = [
        ('prospeccion', 'Prospección'),
        ('primer_contacto', 'Primer Contacto'),
        ('oferta_enviada', 'Oferta Enviada'),
        ('negociacion', 'Negociación'),
        ('contrato', 'Contrato'),
        ('cerrado_ganado', 'Cerrado Ganado'),
        ('cerrado_perdido', 'Cerrado Perdido'),
        ('sin_interes', 'Sin Interés'),
    ]
    ORIGEN = [
        ('externo', 'Externo (Outbound)'),
        ('interno', 'Interno (Inbound)'),
        ('convocatoria', 'Convocatoria Pública'),
    ]

    nombre = models.CharField(max_length=200)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE, related_name='deals')
    tipo_pipeline = models.CharField(max_length=30, choices=TIPO_PIPELINE)
    origen = models.CharField(max_length=20, choices=ORIGEN)
    etapa = models.CharField(max_length=30, choices=ETAPAS, default='prospeccion')
    comercial = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals'
    )
    valor_estimado = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fecha_estimada_cierre = models.DateField(null=True, blank=True)
    probabilidad = models.IntegerField(default=20)
    notas = models.TextField(blank=True)
    motivo_cierre = models.TextField(blank=True)

    # Technical project info
    nombre_proyecto = models.CharField(max_length=200, blank=True)
    tecnologia = models.CharField(max_length=100, blank=True)
    capacidad_instalada_kwp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    generacion_estimada_mwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coordenadas_lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    coordenadas_lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    operador_red = models.CharField(max_length=100, blank=True)

    # RECs specific
    volumen_recs_mwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    periodo_redencion = models.CharField(max_length=100, blank=True)
    registro_irec = models.CharField(max_length=100, blank=True)

    etapa_changed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Deal'
        verbose_name_plural = 'Deals'

    def __str__(self):
        return f"{self.nombre} — {self.cliente.nombre}"

    @property
    def dias_en_etapa(self):
        return (timezone.now() - self.etapa_changed_at).days

    @property
    def is_activo(self):
        return self.etapa in ETAPAS_ACTIVAS


class DealServicio(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='deal_servicios')
    servicio = models.CharField(max_length=30, choices=SERVICIOS_CHOICES)

    class Meta:
        unique_together = ['deal', 'servicio']
        verbose_name = 'Servicio del Deal'
        verbose_name_plural = 'Servicios del Deal'

    def __str__(self):
        return f"{self.deal.nombre} — {self.get_servicio_display()}"


class ActividadDeal(models.Model):
    TIPOS = [
        ('llamada', 'Llamada'),
        ('reunion', 'Reunión'),
        ('email', 'Email'),
        ('nota', 'Nota interna'),
        ('cambio_etapa', 'Cambio de Etapa'),
        ('documento', 'Documento'),
        ('tarea', 'Tarea completada'),
    ]
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='actividades')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Actividad del Deal'
        verbose_name_plural = 'Actividades del Deal'

    def __str__(self):
        return f"[{self.tipo}] {self.deal.nombre} — {self.created_at.date()}"
