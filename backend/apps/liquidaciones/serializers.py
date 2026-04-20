from rest_framework import serializers

from .models import Liquidacion, CostoOperativo


class CostoOperativoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostoOperativo
        fields = '__all__'


class LiquidacionSerializer(serializers.ModelSerializer):
    costos = serializers.SerializerMethodField()

    class Meta:
        model = Liquidacion
        fields = '__all__'

    def get_costos(self, obj):
        from .models import CostoOperativo
        costos = CostoOperativo.objects.filter(
            planta=obj.planta,
            periodo_mes=obj.periodo_mes,
            periodo_anio=obj.periodo_anio,
        )
        return CostoOperativoSerializer(costos, many=True).data


class LiquidacionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liquidacion
        fields = [
            'id',
            'cliente',
            'planta',
            'servicio',
            'periodo_mes',
            'periodo_anio',
            'estado',
            'ingreso_total_cop',
            'margen_cop',
            'margen_pct',
        ]
