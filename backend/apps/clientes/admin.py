from django.contrib import admin

from .models import Cliente, Contacto


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['razon_social', 'nit', 'tipo', 'etapa', 'ciudad', 'creado_en']
    list_filter = ['tipo', 'etapa', 'departamento']
    search_fields = ['razon_social', 'nit', 'email']


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cliente', 'cargo', 'es_decisor', 'email']
    list_filter = ['es_decisor']
    search_fields = ['nombre_completo', 'email']
