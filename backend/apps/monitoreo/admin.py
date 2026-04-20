from django.contrib import admin

from .models import Falla, DatoGeneracion


@admin.register(Falla)
class FallaAdmin(admin.ModelAdmin):
    list_display = ['planta', 'criticidad', 'estado', 'fecha_deteccion', 'centinela']
    list_filter = ['criticidad', 'estado', 'categoria']
    ordering = ['-fecha_deteccion']


@admin.register(DatoGeneracion)
class DatoGeneracionAdmin(admin.ModelAdmin):
    list_display = ['planta', 'fecha', 'energia_kwh', 'fuente', 'validado']
    list_filter = ['fuente', 'validado']
    ordering = ['-fecha']
