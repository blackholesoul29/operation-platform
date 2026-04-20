from django.contrib import admin

from .models import ReporteFrontera, BalanceEnergetico


@admin.register(ReporteFrontera)
class ReporteFronteraAdmin(admin.ModelAdmin):
    list_display = ['planta', 'fecha_reporte', 'estado', 'archivo_nombre', 'subido_en']
    list_filter = ['estado', 'planta']
    ordering = ['-fecha_reporte']


@admin.register(BalanceEnergetico)
class BalanceEnergeticoAdmin(admin.ModelAdmin):
    list_display = ['planta', 'periodo_anio', 'periodo_mes', 'gen_total_kwh', 'fuente', 'validado']
    list_filter = ['fuente', 'validado', 'periodo_anio']
    ordering = ['-periodo_anio', '-periodo_mes']
