from rest_framework import serializers

from .models import Servicio, Planta, ClientePlanta, ClienteServicio, Frontera


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'


class PlantaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = ['id', 'nombre', 'codigo_sic', 'estado', 'potencia_efectiva_kw', 'municipio', 'departamento']


class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = '__all__'


class FronteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frontera
        fields = '__all__'


class ClientePlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientePlanta
        fields = '__all__'


class ClienteServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteServicio
        fields = '__all__'
