from django.contrib import admin

from .models import Servicio, Planta, ClientePlanta, ClienteServicio, Frontera


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'genera_liquidacion_mensual']
    search_fields = ['codigo', 'nombre']


@admin.register(Planta)
class PlantaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_sic', 'estado', 'tecnologia', 'potencia_efectiva_kw', 'municipio', 'departamento']
    list_filter = ['estado', 'tecnologia', 'departamento']
    search_fields = ['nombre', 'codigo_sic']


@admin.register(ClientePlanta)
class ClientePlantaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'planta', 'porcentaje_participacion', 'es_inversionista', 'fecha_inicio', 'fecha_fin']
    list_filter = ['es_inversionista', 'planta']
    search_fields = ['cliente__razon_social', 'planta__nombre']


@admin.register(ClienteServicio)
class ClienteServicioAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'planta', 'servicio', 'estado', 'fecha_inicio', 'fecha_fin']
    list_filter = ['estado', 'servicio', 'planta']
    search_fields = ['cliente__razon_social', 'planta__nombre']


@admin.register(Frontera)
class FronteraAdmin(admin.ModelAdmin):
    list_display = ['planta', 'tipo', 'nombre_frontera', 'codigo_sic', 'operador_red']
    list_filter = ['tipo', 'planta']
    search_fields = ['nombre_frontera', 'codigo_sic', 'planta__nombre']
