from django.db import models
from django.contrib.auth.models import User


class Tarea(models.Model):
    PRIORIDADES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    deal = models.ForeignKey(
        'deals.Deal', on_delete=models.CASCADE,
        null=True, blank=True, related_name='tareas'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente', on_delete=models.CASCADE,
        null=True, blank=True, related_name='tareas'
    )
    asignado_a = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas'
    )
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='tareas_creadas'
    )
    fecha_limite = models.DateTimeField(null=True, blank=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    auto_generada = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completada', 'fecha_limite']
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'

    def __str__(self):
        return self.titulo
