from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    SEGMENTOS = [
        ('industrial', 'Industrial'),
        ('comercial', 'Comercial'),
        ('residencial', 'Residencial'),
        ('gobierno', 'Gobierno'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=20, unique=True)
    segmento = models.CharField(max_length=20, choices=SEGMENTOS, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    departamento = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    notas = models.TextField(blank=True)
    comercial_asignado = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='clientes_asignados'
    )
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} ({self.nit})"


class Contacto(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contactos')
    nombre = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    es_principal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'

    def __str__(self):
        return f"{self.nombre} — {self.cliente.nombre}"
