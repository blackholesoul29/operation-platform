from django.contrib import admin

from .models import IndiceIPP, IndiceIPC, ContratoPPA, GesconAsignacion


@admin.register(IndiceIPP)
class IndiceIPPAdmin(admin.ModelAdmin):
    list_display = ['anio', 'mes', 'valor', 'es_provisional', 'fuente']
    list_filter = ['es_provisional', 'anio']
    ordering = ['-anio', '-mes']


@admin.register(IndiceIPC)
class IndiceIPCAdmin(admin.ModelAdmin):
    list_display = ['anio', 'variacion_anual_pct', 'fuente']
    ordering = ['-anio']


@admin.register(ContratoPPA)
class ContratoPPAAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'planta', 'tipo', 'modalidad', 'estado', 'codigo_contrato', 'fecha_inicio', 'fecha_fin']
    list_filter = ['tipo', 'modalidad', 'estado']
    search_fields = ['codigo_contrato', 'cliente__razon_social', 'planta__nombre']


@admin.register(GesconAsignacion)
class GesconAsignacionAdmin(admin.ModelAdmin):
    list_display = ['planta', 'tipo', 'periodo_anio', 'periodo_mes', 'energia_kwh', 'precio_cop_kwh', 'ingreso_total_cop']
    list_filter = ['tipo', 'planta', 'periodo_anio']
    ordering = ['-periodo_anio', '-periodo_mes']
