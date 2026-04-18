from django.contrib import admin

from .models import Tarea


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'deal', 'cliente', 'asignado_a', 'prioridad',
        'completada', 'fecha_limite', 'auto_generada', 'created_at'
    ]
    list_filter = ['completada', 'prioridad', 'auto_generada']
    search_fields = ['titulo', 'deal__nombre', 'cliente__nombre']
    readonly_fields = ['created_at', 'updated_at', 'fecha_completada']
