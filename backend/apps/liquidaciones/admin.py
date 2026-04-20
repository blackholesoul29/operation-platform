from django.contrib import admin

from .models import Liquidacion, CostoOperativo


@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'planta', 'periodo_mes', 'periodo_anio', 'estado', 'margen_cop']
    list_filter = ['estado', 'periodo_anio', 'servicio']
    ordering = ['-periodo_anio', '-periodo_mes']


@admin.register(CostoOperativo)
class CostoOperativoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'planta', 'valor_cop', 'fecha']
    list_filter = ['tipo']
    ordering = ['-fecha']
