from django.db import models


class Cliente(models.Model):
    TIPO_CHOICES = [
        ('EMPRESA', 'Empresa'),
        ('PERSONA_NATURAL', 'Persona Natural'),
    ]
    ETAPA_CHOICES = [
        ('LEAD', 'Lead'),
        ('PROSPECTO', 'Prospecto'),
        ('CONTACTO', 'Contacto'),
        ('NEGOCIACION', 'Negociación'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('CHURNED', 'Churned'),
    ]

    razon_social = models.CharField(max_length=255, unique=True)
    nit = models.CharField(max_length=20, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    etapa = models.CharField(max_length=20, choices=ETAPA_CHOICES, default='LEAD')
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    google_drive_folder_id = models.CharField(max_length=200, blank=True)
    google_drive_folder_url = models.URLField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['razon_social']

    def __str__(self):
        return self.razon_social


class Contacto(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='contactos',
    )
    nombre_completo = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)
    es_decisor = models.BooleanField(default=False)
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'

    def __str__(self):
        return f"{self.nombre_completo} - {self.cliente.razon_social}"
