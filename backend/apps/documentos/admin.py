from django.contrib import admin

from .models import TipoDocumento, DocumentoRequerido, Documento


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo', 'tiene_vencimiento']
    search_fields = ['nombre', 'codigo']


@admin.register(DocumentoRequerido)
class DocumentoRequeridoAdmin(admin.ModelAdmin):
    list_display = ['tipo_documento', 'servicio', 'obligatorio']
    list_filter = ['servicio', 'obligatorio']


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'tipo_documento', 'cliente', 'deal',
        'estado', 'version', 'fecha_vencimiento', 'subido_por', 'created_at'
    ]
    list_filter = ['estado', 'tipo_documento']
    search_fields = ['nombre', 'cliente__nombre', 'deal__nombre']
    readonly_fields = ['version', 'archivo_nombre_original', 'archivo_tamanio', 'archivo_tipo_mime', 'created_at', 'updated_at']
