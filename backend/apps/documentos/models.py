from django.db import models


class Documento(models.Model):
    class TipoDocumento(models.TextChoices):
        # Comerciales / legales
        CONTRATO = 'CONTRATO', 'Contrato'
        NDA = 'NDA', 'NDA'
        PROPUESTA = 'PROPUESTA', 'Propuesta'
        ACUERDO = 'ACUERDO', 'Acuerdo'
        # Técnicos de planta
        HOJA_VIDA_PLANTA = 'HOJA_VIDA_PLANTA', 'Hoja de Vida Planta'
        CERT_MEDIDOR = 'CERT_MEDIDOR', 'Certificado Medidor'
        CERT_CALIBRACION = 'CERT_CALIBRACION', 'Certificado Calibración'
        CERT_CT_PT = 'CERT_CT_PT', 'Certificado CT/PT'
        UNIFILAR = 'UNIFILAR', 'Unifilar'
        REGISTRO_XM = 'REGISTRO_XM', 'Registro XM'
        REGISTRO_CND = 'REGISTRO_CND', 'Registro CND'
        COORD_PROTECCIONES = 'COORD_PROTECCIONES', 'Coord. Protecciones'
        CERT_CONEXION = 'CERT_CONEXION', 'Certificado de Conexión'
        INDISPONIBILIDADES = 'INDISPONIBILIDADES', 'Indisponibilidades'
        # Operativos / financieros
        REPORTE_FRONTERA = 'REPORTE_FRONTERA', 'Reporte de Frontera'
        MANDATO = 'MANDATO', 'Mandato'
        FACTURA = 'FACTURA', 'Factura'
        OTRO = 'OTRO', 'Otro'

    nombre = models.CharField(max_length=300)
    tipo = models.CharField(
        max_length=30,
        choices=TipoDocumento.choices,
        default=TipoDocumento.OTRO,
    )
    descripcion = models.TextField(blank=True)

    # Archivo local (opcional)
    archivo = models.FileField(
        upload_to='documentos/%Y/%m/',
        null=True,
        blank=True,
    )

    # Google Drive
    google_drive_id = models.CharField(max_length=200, blank=True)
    google_drive_url = models.URLField(blank=True)

    # FKs opcionales — el documento puede pertenecer a uno o varios de estos
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.CASCADE,
        related_name='documentos',
        null=True,
        blank=True,
    )
    planta = models.ForeignKey(
        'proyectos.Planta',
        on_delete=models.CASCADE,
        related_name='documentos',
        null=True,
        blank=True,
    )
    frontera = models.ForeignKey(
        'proyectos.Frontera',
        on_delete=models.CASCADE,
        related_name='documentos',
        null=True,
        blank=True,
    )
    liquidacion = models.ForeignKey(
        'liquidaciones.Liquidacion',
        on_delete=models.CASCADE,
        related_name='documentos',
        null=True,
        blank=True,
    )

    subido_en = models.DateTimeField(auto_now_add=True)
    subido_por = models.CharField(max_length=200, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-subido_en']

    def __str__(self):
        return f"{self.tipo} | {self.nombre}"
