from django.db import models
from django.contrib.auth.models import User
from apps.deals.models import SERVICIOS_CHOICES


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    tiene_vencimiento = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class DocumentoRequerido(models.Model):
    servicio = models.CharField(max_length=30, choices=SERVICIOS_CHOICES)
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.CASCADE, related_name='requerido_para'
    )
    obligatorio = models.BooleanField(default=True)

    class Meta:
        unique_together = ['servicio', 'tipo_documento']
        verbose_name = 'Documento Requerido'
        verbose_name_plural = 'Documentos Requeridos'

    def __str__(self):
        return f"{self.tipo_documento.nombre} para {self.servicio}"


class Documento(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('recibido', 'Recibido'),
        ('aprobado', 'Aprobado'),
        ('vencido', 'Vencido'),
        ('rechazado', 'Rechazado'),
    ]
    cliente = models.ForeignKey(
        'clientes.Cliente', on_delete=models.CASCADE,
        null=True, blank=True, related_name='documentos'
    )
    deal = models.ForeignKey(
        'deals.Deal', on_delete=models.CASCADE,
        null=True, blank=True, related_name='documentos'
    )
    tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='documentos/%Y/%m/')
    archivo_nombre_original = models.CharField(max_length=200, blank=True)
    archivo_tamanio = models.BigIntegerField(null=True, blank=True)
    archivo_tipo_mime = models.CharField(max_length=100, blank=True)
    version = models.IntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='recibido')
    fecha_vencimiento = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f"{self.nombre} v{self.version}"

    def save(self, *args, **kwargs):
        if not self.pk and self.tipo_documento:
            qs = Documento.objects.filter(
                deal=self.deal, cliente=self.cliente,
                tipo_documento=self.tipo_documento
            )
            self.version = qs.count() + 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.archivo:
            import os
            try:
                if os.path.isfile(self.archivo.path):
                    os.remove(self.archivo.path)
            except Exception:
                pass
        super().delete(*args, **kwargs)
