from django.contrib import admin

from .models import Deal, DealServicio, ActividadDeal


class DealServicioInline(admin.TabularInline):
    model = DealServicio
    extra = 1


class ActividadDealInline(admin.TabularInline):
    model = ActividadDeal
    extra = 0
    readonly_fields = ['tipo', 'descripcion', 'creado_por', 'created_at']
    can_delete = False


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'cliente', 'tipo_pipeline', 'etapa',
        'comercial', 'valor_estimado', 'probabilidad', 'created_at'
    ]
    list_filter = ['etapa', 'tipo_pipeline', 'origen', 'comercial']
    search_fields = ['nombre', 'cliente__nombre', 'cliente__nit']
    readonly_fields = ['etapa_changed_at', 'created_at', 'updated_at', 'dias_en_etapa']
    inlines = [DealServicioInline, ActividadDealInline]
    fieldsets = (
        ('Información Principal', {
            'fields': (
                'nombre', 'cliente', 'tipo_pipeline', 'origen',
                'etapa', 'comercial', 'valor_estimado',
                'fecha_estimada_cierre', 'probabilidad', 'notas', 'motivo_cierre',
            )
        }),
        ('Información Técnica', {
            'fields': (
                'nombre_proyecto', 'tecnologia', 'capacidad_instalada_kwp',
                'generacion_estimada_mwh', 'coordenadas_lat', 'coordenadas_lng',
                'operador_red',
            ),
            'classes': ['collapse'],
        }),
        ('RECs', {
            'fields': ('volumen_recs_mwh', 'periodo_redencion', 'registro_irec'),
            'classes': ['collapse'],
        }),
        ('Auditoría', {
            'fields': ('etapa_changed_at', 'created_at', 'updated_at', 'dias_en_etapa'),
            'classes': ['collapse'],
        }),
    )


@admin.register(DealServicio)
class DealServicioAdmin(admin.ModelAdmin):
    list_display = ['deal', 'servicio']
    list_filter = ['servicio']


@admin.register(ActividadDeal)
class ActividadDealAdmin(admin.ModelAdmin):
    list_display = ['deal', 'tipo', 'creado_por', 'created_at']
    list_filter = ['tipo']
    search_fields = ['deal__nombre', 'descripcion']
    readonly_fields = ['created_at']
