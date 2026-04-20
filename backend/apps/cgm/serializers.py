from rest_framework import serializers

from .models import ReporteFrontera, BalanceEnergetico


class ReporteFronteraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteFrontera
        fields = '__all__'


class BalanceEnergeticoSerializer(serializers.ModelSerializer):
    balance_neto_kwh = serializers.SerializerMethodField()

    class Meta:
        model = BalanceEnergetico
        fields = '__all__'

    def get_balance_neto_kwh(self, obj):
        return obj.balance_neto_kwh
