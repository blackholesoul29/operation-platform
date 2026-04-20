from django.db import models


class ReporteFrontera(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        SUBIDO = 'SUBIDO', 'Subido'
        VALIDADO = 'VALIDADO', 'Validado'

    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='reportes_frontera',
    )
    fecha_reporte = models.DateField(help_text='Día del reporte')
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    archivo_nombre = models.CharField(max_length=300, blank=True)
    google_drive_id = models.CharField(max_length=200, blank=True)
    google_drive_url = models.URLField(blank=True)
    observaciones = models.TextField(blank=True)
    subido_en = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reporte de Frontera'
        verbose_name_plural = 'Reportes de Frontera'
        unique_together = ['planta', 'fecha_reporte']
        ordering = ['-fecha_reporte']

    def __str__(self):
        return f"{self.planta} | {self.fecha_reporte} | {self.estado}"


class BalanceEnergetico(models.Model):
    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='balance_energetico',
    )
    periodo_mes = models.IntegerField()
    periodo_anio = models.IntegerField()

    gen_ppa_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, default=0
    )
    gen_bolsa_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, default=0
    )
    gen_interna_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, default=0
    )
    compras_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, default=0
    )
    gen_total_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, default=0,
        help_text='Campo calculado que se puede pre-computar',
    )

    fuente = models.CharField(
        max_length=100,
        default='MANUAL',
        help_text='XM, SUNFACTORY, MANUAL, EXCEL',
    )
    validado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Balance Energético'
        verbose_name_plural = 'Balances Energéticos'
        unique_together = ['planta', 'periodo_mes', 'periodo_anio']
        ordering = ['-periodo_anio', '-periodo_mes']

    def __str__(self):
        return f"{self.planta} | {self.periodo_anio}/{str(self.periodo_mes).zfill(2)}"

    @property
    def balance_neto_kwh(self):
        return self.gen_total_kwh - self.compras_kwh
