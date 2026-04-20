from datetime import datetime

from rest_framework import serializers

from .models import IndiceIPP, IndiceIPC, ContratoPPA, GesconAsignacion


class IndiceIPPSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndiceIPP
        fields = '__all__'


class IndiceIPCSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndiceIPC
        fields = '__all__'


class ContratoPPASerializer(serializers.ModelSerializer):
    tarifa_ppa_efectiva_actual = serializers.SerializerMethodField()
    tarifa_cgm_efectiva_actual = serializers.SerializerMethodField()

    class Meta:
        model = ContratoPPA
        fields = '__all__'

    def get_tarifa_ppa_efectiva_actual(self, obj):
        hoy = datetime.today()
        resultado = obj.tarifa_efectiva_ppa(hoy.year, hoy.month)
        return str(resultado) if resultado is not None else None

    def get_tarifa_cgm_efectiva_actual(self, obj):
        hoy = datetime.today()
        resultado = obj.tarifa_efectiva_cgm(hoy.year)
        return str(resultado) if resultado is not None else None


class GesconAsignacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GesconAsignacion
        fields = '__all__'
