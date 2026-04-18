from django.db import models
from django.contrib.auth.models import User


class Notificacion(models.Model):
    TIPOS = [
        ('documento_vencido', 'Documento Vencido'),
        ('documento_por_vencer', 'Documento por Vencer'),
        ('seguimiento_pendiente', 'Seguimiento Pendiente'),
        ('deal_estancado', 'Deal Estancado'),
        ('contrato_sin_firma', 'Contrato sin Firma'),
        ('tarea_vencida', 'Tarea Vencida'),
        ('general', 'General'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=30, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    deal = models.ForeignKey(
        'deals.Deal', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notificaciones'
    )
    cliente = models.ForeignKey(
        'clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notificaciones'
    )
    documento = models.ForeignKey(
        'documentos.Documento', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"[{self.tipo}] {self.titulo} -> {self.usuario.username}"
