from rest_framework import serializers

from .models import Cliente, Contacto


class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    contactos = ContactoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'


class ClienteListSerializer(serializers.ModelSerializer):
    # versión ligera para listas
    class Meta:
        model = Cliente
        fields = ['id', 'razon_social', 'nit', 'tipo', 'etapa', 'email', 'ciudad']
