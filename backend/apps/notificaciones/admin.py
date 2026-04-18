from django.contrib import admin

from .models import Notificacion


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'leida', 'deal', 'cliente', 'created_at']
    list_filter = ['tipo', 'leida']
    search_fields = ['titulo', 'mensaje', 'usuario__username']
    readonly_fields = ['created_at']
    list_editable = ['leida']
