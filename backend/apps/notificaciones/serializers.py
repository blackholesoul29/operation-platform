from rest_framework import serializers

from .models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    deal = serializers.SerializerMethodField()
    cliente = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        fields = [
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje',
            'leida', 'deal', 'cliente', 'created_at',
        ]
        read_only_fields = ['id', 'tipo', 'titulo', 'mensaje', 'created_at']

    def get_deal(self, obj):
        if obj.deal:
            return {'id': obj.deal.id, 'nombre': obj.deal.nombre}
        return None

    def get_cliente(self, obj):
        if obj.cliente:
            return {'id': obj.cliente.id, 'nombre': obj.cliente.nombre}
        return None
