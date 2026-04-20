from rest_framework import serializers

from .models import Documento


class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'


class DocumentoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ['id', 'nombre', 'tipo', 'cliente', 'planta', 'google_drive_url', 'subido_en']
