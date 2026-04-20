from django.contrib import admin

from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'cliente', 'planta', 'subido_en']
    list_filter = ['tipo']
    ordering = ['-subido_en']
