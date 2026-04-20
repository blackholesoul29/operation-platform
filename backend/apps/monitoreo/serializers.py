from rest_framework import serializers

from .models import Falla, DatoGeneracion


class FallaSerializer(serializers.ModelSerializer):
    duracion_horas = serializers.SerializerMethodField()

    class Meta:
        model = Falla
        fields = '__all__'

    def get_duracion_horas(self, obj):
        if obj.fecha_resolucion and obj.fecha_deteccion:
            delta = obj.fecha_resolucion - obj.fecha_deteccion
            return round(delta.total_seconds() / 3600, 2)
        return None


class DatoGeneracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatoGeneracion
        fields = '__all__'
