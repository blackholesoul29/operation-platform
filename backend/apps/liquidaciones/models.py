from django.db import models


class CostoOperativo(models.Model):
    class TipoCosto(models.TextChoices):
        MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'
        ARRIENDO = 'ARRIENDO', 'Arriendo'
        INTERNET = 'INTERNET', 'Internet'
        COMUNICACIONES = 'COMUNICACIONES', 'Comunicaciones'
        SEGUROS = 'SEGUROS', 'Seguros'
        OTRO = 'OTRO', 'Otro'

    tipo = models.CharField(
        max_length=20,
        choices=TipoCosto.choices,
        default=TipoCosto.OTRO,
    )
    descripcion = models.CharField(max_length=300)
    valor_cop = models.DecimalField(max_digits=15, decimal_places=2)
    fecha = models.DateField()
    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='costos_operativos',
        null=True,
        blank=True,
    )
    periodo_mes = models.IntegerField(null=True, blank=True)
    periodo_anio = models.IntegerField(null=True, blank=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Costo Operativo'
        verbose_name_plural = 'Costos Operativos'
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.tipo} | {self.valor_cop} COP | {self.fecha}"


class Liquidacion(models.Model):
    class LiquidacionEstado(models.TextChoices):
        RECOPILACION = 'RECOPILACION', 'Recopilación'
        FACTURACION_ENERGIA = 'FACTURACION_ENERGIA', 'Facturación Energía'
        CONTABILIZACION = 'CONTABILIZACION', 'Contabilización'
        MANDATOS = 'MANDATOS', 'Mandatos'
        ENTREGADO = 'ENTREGADO', 'Entregado'

    # Vínculos principales
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='liquidaciones',
    )
    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='liquidaciones',
    )
    servicio = models.ForeignKey(
        'proyectos.Servicio',
        on_delete=models.CASCADE,
        related_name='liquidaciones',
        null=True,
        blank=True,
    )

    # Periodo
    periodo_mes = models.IntegerField()   # 1–12
    periodo_anio = models.IntegerField()

    # Estado
    estado = models.CharField(
        max_length=30,
        choices=LiquidacionEstado.choices,
        default=LiquidacionEstado.RECOPILACION,
    )
    fecha_estado_actual = models.DateField(null=True, blank=True)

    # --- Energía (datos de XM/ASIC via GESCON) ---
    gen_total_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True
    )
    gen_ppa_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True
    )
    gen_bolsa_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True
    )
    gen_interna_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True
    )
    compras_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True,
        help_text='Consumo auxiliar comprado al mercado',
    )
    precio_bolsa_promedio_cop = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )

    # --- Ingresos ---
    ingreso_ppa_cop = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    ingreso_bolsa_cop = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    ingreso_servicios_cop = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True,
        help_text='Fees de REP + CGM + OM',
    )
    ingreso_total_cop = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    # --- Costos ---
    costo_total_cop = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True,
        help_text='Relacionado con CostoOperativo vía planta + periodo',
    )

    # --- Resultado ---
    margen_cop = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    margen_pct = models.DecimalField(
        max_digits=6, decimal_places=4, null=True, blank=True
    )

    # --- Tarifas efectivas aplicadas al momento de liquidar ---
    tarifa_ppa_aplicada_cop_kwh = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    tarifa_rep_aplicada_cop_kwh = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    tarifa_cgm_aplicada_cop_kwh = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )

    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Liquidación'
        verbose_name_plural = 'Liquidaciones'
        unique_together = ['cliente', 'planta', 'periodo_mes', 'periodo_anio']
        ordering = ['-periodo_anio', '-periodo_mes']

    def __str__(self):
        return (
            f"{self.cliente} | {self.planta} | "
            f"{self.periodo_anio}/{str(self.periodo_mes).zfill(2)}"
        )
