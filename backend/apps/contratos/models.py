from decimal import Decimal

from django.db import models


class IndiceIPP(models.Model):
    anio = models.IntegerField()
    mes = models.IntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=6)
    es_provisional = models.BooleanField(default=True)
    fuente = models.CharField(max_length=100, default='DANE')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Índice IPP'
        verbose_name_plural = 'Índices IPP'
        unique_together = ['anio', 'mes']
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"IPP {self.anio}/{self.mes:02d} = {self.valor}"


class IndiceIPC(models.Model):
    anio = models.IntegerField(unique=True)
    variacion_anual_pct = models.DecimalField(max_digits=6, decimal_places=4)
    fuente = models.CharField(max_length=100, default='DANE')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Índice IPC'
        verbose_name_plural = 'Índices IPC'
        ordering = ['-anio']

    def __str__(self):
        return f"IPC {self.anio} = {self.variacion_anual_pct}%"


class ContratoPPA(models.Model):
    TIPO_CHOICES = [
        ('VENTA', 'Venta (Unergy vende al cliente)'),
        ('COMPRA', 'Compra (Unergy compra al cliente)'),
    ]
    MODALIDAD_CHOICES = [
        ('BOLSA', 'Bolsa'),
        ('PPA', 'PPA'),
        ('INTERNO', 'Interno'),
    ]
    ESTADO_CHOICES = [
        ('NEGOCIACION', 'Negociación'),
        ('ACTIVO', 'Activo'),
        ('VENCIDO', 'Vencido'),
        ('TERMINADO', 'Terminado'),
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='contratos_ppa',
    )
    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='contratos_ppa',
        null=True,
        blank=True,
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    codigo_contrato = models.CharField(max_length=100, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    # Tarifa PPA indexada a IPP
    tarifa_base_cop_kwh = models.DecimalField(max_digits=12, decimal_places=4)
    ipp_base = models.DecimalField(max_digits=12, decimal_places=6)
    anio_ipp_base = models.IntegerField(null=True, blank=True)
    mes_ipp_base = models.IntegerField(null=True, blank=True)

    # Tarifas CGM/REP indexadas a IPC anual
    tarifa_cgm_cop_kwh = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    tarifa_rep_cop_kwh = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    anio_ultima_actualizacion_ipc = models.IntegerField(null=True, blank=True)

    volumen_comprometido_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True
    )
    modalidad = models.CharField(max_length=10, choices=MODALIDAD_CHOICES, default='PPA')
    registrado_asic = models.BooleanField(default=False)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='NEGOCIACION')
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contrato PPA'
        verbose_name_plural = 'Contratos PPA'

    def __str__(self):
        return f"{self.cliente} | {self.tipo} | {self.fecha_inicio}"

    def tarifa_efectiva_ppa(self, anio, mes):
        """
        Retorna la tarifa PPA ajustada por IPP para el período (anio, mes).
        Formula: tarifa_base * (IPP_periodo / IPP_base)
        Si no existe el IPP o ipp_base es 0, retorna tarifa_base.
        """
        if not self.ipp_base or self.ipp_base == Decimal('0'):
            return self.tarifa_base_cop_kwh
        try:
            ipp_periodo = IndiceIPP.objects.get(anio=anio, mes=mes)
        except IndiceIPP.DoesNotExist:
            return self.tarifa_base_cop_kwh
        return self.tarifa_base_cop_kwh * (ipp_periodo.valor / self.ipp_base)

    def tarifa_efectiva_cgm(self, anio):
        """
        Retorna la tarifa CGM ajustada por IPC compuesto desde
        anio_ultima_actualizacion_ipc hasta anio (exclusive).
        Formula: tarifa_cgm * prod(1 + ipc_pct/100) para cada año intermedio.
        """
        if not self.tarifa_cgm_cop_kwh:
            return Decimal('0')
        anio_base = self.anio_ultima_actualizacion_ipc
        if not anio_base or anio <= anio_base:
            return self.tarifa_cgm_cop_kwh
        indices = IndiceIPC.objects.filter(
            anio__gt=anio_base,
            anio__lte=anio,
        ).order_by('anio')
        factor = Decimal('1')
        for ipc in indices:
            factor *= Decimal('1') + (ipc.variacion_anual_pct / Decimal('100'))
        return self.tarifa_cgm_cop_kwh * factor


class GesconAsignacion(models.Model):
    TIPO_CHOICES = [
        ('BOLSA', 'Bolsa'),
        ('PPA', 'PPA'),
        ('INTERNO', 'Interno'),
    ]

    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='asignaciones_gescon',
    )
    contrato_ppa = models.ForeignKey(
        ContratoPPA,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        null=True,
        blank=True,
    )
    periodo_mes = models.IntegerField()
    periodo_anio = models.IntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    energia_kwh = models.DecimalField(max_digits=15, decimal_places=3)
    precio_cop_kwh = models.DecimalField(max_digits=12, decimal_places=4)
    ingreso_total_cop = models.DecimalField(max_digits=18, decimal_places=2)
    agente_contraparte = models.CharField(max_length=200, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Asignación Gescon'
        verbose_name_plural = 'Asignaciones Gescon'
        unique_together = ['planta', 'contrato_ppa', 'periodo_mes', 'periodo_anio', 'tipo']

    def __str__(self):
        return (
            f"{self.planta} | {self.tipo} | "
            f"{self.periodo_anio}/{self.periodo_mes:02d} | {self.energia_kwh} kWh"
        )
