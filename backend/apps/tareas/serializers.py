from django.utils import timezone
from rest_framework import serializers

from .models import Tarea


def _user_mini(user):
    if not user:
        return None
    full_name = ''
    if hasattr(user, 'profile'):
        full_name = user.profile.full_name
    else:
        full_name = user.get_full_name() or user.username
    return {'id': user.id, 'full_name': full_name}


class TareaListSerializer(serializers.ModelSerializer):
    deal = serializers.SerializerMethodField()
    cliente = serializers.SerializerMethodField()
    asignado_a = serializers.SerializerMethodField()
    creado_por = serializers.SerializerMethodField()
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    es_vencida = serializers.SerializerMethodField()

    class Meta:
        model = Tarea
        fields = [
            'id', 'titulo', 'descripcion', 'deal', 'cliente',
            'asignado_a', 'creado_por', 'fecha_limite',
            'prioridad', 'prioridad_display', 'completada',
            'fecha_completada', 'auto_generada', 'es_vencida', 'created_at',
        ]

    def get_deal(self, obj):
        if obj.deal:
            return {'id': obj.deal.id, 'nombre': obj.deal.nombre}
        return None

    def get_cliente(self, obj):
        if obj.cliente:
            return {'id': obj.cliente.id, 'nombre': obj.cliente.nombre}
        return None

    def get_asignado_a(self, obj):
        return _user_mini(obj.asignado_a)

    def get_creado_por(self, obj):
        return _user_mini(obj.creado_por)

    def get_es_vencida(self, obj):
        if obj.completada or not obj.fecha_limite:
            return False
        return obj.fecha_limite < timezone.now()


class TareaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = [
            'titulo', 'descripcion', 'deal', 'cliente',
            'asignado_a', 'fecha_limite', 'prioridad',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        creado_por = request.user if request else None
        return Tarea.objects.create(creado_por=creado_por, **validated_data)
