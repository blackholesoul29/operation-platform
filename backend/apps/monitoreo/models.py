from django.db import models


class Falla(models.Model):
    class Criticidad(models.TextChoices):
        CRITICA = 'CRITICA', 'Crítica'
        MEDIA = 'MEDIA', 'Media'
        BAJA = 'BAJA', 'Baja'

    class Estado(models.TextChoices):
        ABIERTA = 'ABIERTA', 'Abierta'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        RESUELTA = 'RESUELTA', 'Resuelta'
        CERRADA = 'CERRADA', 'Cerrada'

    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='fallas',
    )
    codigo_falla = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField()
    categoria = models.CharField(
        max_length=100,
        blank=True,
        help_text='Ej: Inversor, Módulos, Comunicaciones',
    )
    criticidad = models.CharField(
        max_length=20,
        choices=Criticidad.choices,
        default=Criticidad.MEDIA,
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ABIERTA,
    )
    fecha_deteccion = models.DateTimeField()
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    centinela = models.CharField(
        max_length=200,
        blank=True,
        help_text='Quién registró la falla',
    )
    causa_raiz = models.TextField(blank=True)
    solucion = models.TextField(blank=True)
    impacto_kwh = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Energía perdida estimada en kWh',
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Falla'
        verbose_name_plural = 'Fallas'
        ordering = ['-fecha_deteccion']

    def __str__(self):
        return f"[{self.criticidad}] {self.planta} | {self.descripcion[:60]}"


class DatoGeneracion(models.Model):
    class Fuente(models.TextChoices):
        XM = 'XM', 'XM'
        SUNFACTORY = 'SUNFACTORY', 'SunFactory'
        INTERNO = 'INTERNO', 'Interno'
        EXCEL = 'EXCEL', 'Excel'

    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='datos_generacion',
    )
    fecha = models.DateField()
    energia_kwh = models.DecimalField(max_digits=15, decimal_places=3)
    potencia_peak_kw = models.DecimalField(
        max_digits=12, decimal_places=3, null=True, blank=True
    )
    irradiancia_kwh_m2 = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    temperatura_modulo_c = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    performance_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='Rango 0.0 a 1.0',
    )
    fuente = models.CharField(
        max_length=20,
        choices=Fuente.choices,
        default=Fuente.XM,
    )
    validado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dato de Generación'
        verbose_name_plural = 'Datos de Generación'
        unique_together = ['planta', 'fecha', 'fuente']
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.planta} | {self.fecha} | {self.energia_kwh} kWh"
