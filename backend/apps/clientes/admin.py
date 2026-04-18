from django.contrib import admin

from .models import Cliente, Contacto


class ContactoInline(admin.TabularInline):
    model = Contacto
    extra = 1
    fields = ['nombre', 'cargo', 'email', 'telefono', 'es_principal']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nit', 'segmento', 'ciudad', 'comercial_asignado', 'activo', 'created_at']
    list_filter = ['segmento', 'activo', 'comercial_asignado']
    search_fields = ['nombre', 'nit', 'ciudad']
    inlines = [ContactoInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cliente', 'cargo', 'email', 'telefono', 'es_principal']
    list_filter = ['es_principal']
    search_fields = ['nombre', 'email', 'cliente__nombre']
