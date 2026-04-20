from django.db import models


class Servicio(models.Model):
    CODIGO_CHOICES = [
        ('REP', 'REP'),
        ('CGM', 'CGM'),
        ('PROMOTOR', 'Promotor'),
        ('OM', 'O&M'),
        ('PPA_VENTA', 'PPA Venta'),
        ('PPA_COMPRA', 'PPA Compra'),
    ]

    codigo = models.CharField(max_length=20, unique=True, choices=CODIGO_CHOICES)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    genera_liquidacion_mensual = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Planta(models.Model):
    ESTADO_CHOICES = [
        ('CONSTRUCCION', 'Construcción'),
        ('PRUEBAS', 'Pruebas'),
        ('OPERANDO', 'Operando'),
        ('SUSPENDIDA', 'Suspendida'),
    ]
    TECNOLOGIA_CHOICES = [
        ('SOLAR', 'Solar'),
        ('EOLICA', 'Eólica'),
        ('HIDRO', 'Hidro'),
    ]

    nombre = models.CharField(max_length=200)
    codigo_sic = models.CharField(max_length=50, blank=True)
    potencia_instalada_kwp = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    potencia_efectiva_kw = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    fecha_inicio_pruebas = models.DateField(null=True, blank=True)
    fecha_inicio_operacion = models.DateField(null=True, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    altitud_msnm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='CONSTRUCCION')
    tecnologia = models.CharField(max_length=20, choices=TECNOLOGIA_CHOICES, default='SOLAR')
    clasificacion_recurso = models.CharField(max_length=100, blank=True)
    operador_red = models.CharField(max_length=200, blank=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Planta'
        verbose_name_plural = 'Plantas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ClientePlanta(models.Model):
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='participaciones',
    )
    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='participaciones',
    )
    porcentaje_participacion = models.DecimalField(max_digits=5, decimal_places=2)
    es_inversionista = models.BooleanField(default=False)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente-Planta'
        verbose_name_plural = 'Clientes-Plantas'
        unique_together = ['cliente', 'planta', 'fecha_inicio']

    def __str__(self):
        return f"{self.cliente} → {self.planta} {self.porcentaje_participacion}%"


class ClienteServicio(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='servicios_contratados',
    )
    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='servicios',
        null=True,
        blank=True,
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='clientes',
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    tarifa_base_cop = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True
    )
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente-Servicio'
        verbose_name_plural = 'Clientes-Servicios'

    def __str__(self):
        return f"{self.cliente} | {self.servicio} | {self.planta}"


class Frontera(models.Model):
    TIPO_CHOICES = [
        ('GENERACION', 'Generación'),
        ('CONSUMO', 'Consumo'),
    ]

    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='fronteras',
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    # Identificación
    codigo_sic = models.CharField(max_length=100, blank=True)
    nombre_frontera = models.CharField(max_length=300, blank=True)
    codigo_propio = models.CharField(max_length=100, blank=True)
    registrada_mercado_por = models.CharField(max_length=200, blank=True)
    registrada_primera_vez = models.DateField(null=True, blank=True)
    factor_perdidas = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)

    # Datos del usuario/propietario
    niu = models.CharField(max_length=100, blank=True)
    nit_frontera = models.CharField(max_length=50, blank=True)
    voltaje_kv = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    nivel_tension = models.CharField(max_length=50, blank=True)
    tipo_punto_medicion = models.CharField(max_length=100, blank=True)
    transferencia_maxima_kwh = models.DecimalField(
        max_digits=15, decimal_places=3, null=True, blank=True
    )

    # Representación
    representante_frontera = models.CharField(max_length=200, blank=True)
    inicio_representacion = models.DateField(null=True, blank=True)
    representante_anterior = models.CharField(max_length=200, blank=True)

    # Red
    operador_red = models.CharField(max_length=200, blank=True)
    operador_red_zona = models.CharField(max_length=200, blank=True)

    # Agentes
    agente_exportador = models.CharField(max_length=200, blank=True)
    agente_importador = models.CharField(max_length=200, blank=True)

    # Tipo y capacidades
    tipo_frontera = models.CharField(max_length=100, blank=True)
    capacidad_transporte_mw = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    capacidad_transporte_acc_mw = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    capacidad_efectiva_mw = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )

    # CGM / DDV
    nombre_cgm = models.CharField(max_length=200, blank=True)
    codigo_sic_ddv = models.CharField(max_length=100, blank=True)
    predio_id = models.CharField(max_length=100, blank=True)
    nombre_predio = models.CharField(max_length=300, blank=True)
    representante_ddv = models.CharField(max_length=200, blank=True)

    # Medidor principal
    serie_med_ppal = models.CharField(max_length=100, blank=True)
    marca_med_ppal = models.CharField(max_length=100, blank=True)
    modelo_med_ppal = models.CharField(max_length=100, blank=True)
    clase_medidor = models.CharField(max_length=50, blank=True)
    num_elementos_ppal = models.IntegerField(null=True, blank=True)
    clase_ct = models.CharField(max_length=50, blank=True)
    clase_pt = models.CharField(max_length=50, blank=True)
    ultimo_cambio_med_ppal = models.DateField(null=True, blank=True)
    entidad_calibradora_ppal = models.CharField(max_length=200, blank=True)
    fecha_calibracion_ppal = models.DateField(null=True, blank=True)
    ppal_actualizada = models.DateField(null=True, blank=True)

    # Medidor respaldo
    serie_med_resp = models.CharField(max_length=100, blank=True)
    marca_med_resp = models.CharField(max_length=100, blank=True)
    modelo_med_resp = models.CharField(max_length=100, blank=True)
    num_elementos_resp = models.IntegerField(null=True, blank=True)
    ultimo_cambio_med_resp = models.DateField(null=True, blank=True)
    entidad_calibradora_resp = models.CharField(max_length=200, blank=True)
    fecha_calibracion_resp = models.DateField(null=True, blank=True)
    resp_actualizada = models.DateField(null=True, blank=True)

    # Agrupación y modelo embebido
    es_agrupadora = models.BooleanField(default=False)
    factor_psf = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    agrupada_bajo = models.CharField(max_length=200, blank=True)
    es_principal_modelo_embebido = models.BooleanField(default=False)
    embebida_bajo = models.CharField(max_length=200, blank=True)

    # Factores
    factor_acordado = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    factor_ajuste = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    factor_perdidas_frontera_ppal = models.DecimalField(
        max_digits=8, decimal_places=6, null=True, blank=True
    )

    # Clasificación industrial
    codigo_ciiu = models.CharField(max_length=20, blank=True)
    clasificacion_industrial_general = models.CharField(max_length=200, blank=True)
    clasificacion_industrial_especifica = models.CharField(max_length=200, blank=True)

    # Ubicación
    departamento = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    centro_poblado = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    altitud_msnm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Submercado / generación / usuario
    codigo_sic_submercado_exp = models.CharField(max_length=100, blank=True)
    codigo_sic_frontera_generacion = models.CharField(max_length=100, blank=True)
    nombre_recurso_generacion = models.CharField(max_length=300, blank=True)
    clasificacion_recurso = models.CharField(max_length=100, blank=True)
    capacidad_efectiva_potencia_max = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True
    )
    tipo_tecnologia = models.CharField(max_length=100, blank=True)
    codigo_sic_frontera_usuario = models.CharField(max_length=100, blank=True)
    codigo_sic_submercado_consumo = models.CharField(max_length=100, blank=True)
    codigo_sic_submercado_usuario = models.CharField(max_length=100, blank=True)

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Frontera'
        verbose_name_plural = 'Fronteras'

    def __str__(self):
        return f"{self.planta} - {self.tipo} - {self.nombre_frontera}"
