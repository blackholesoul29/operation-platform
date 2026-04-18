from rest_framework import serializers

from .models import Cliente, Contacto


class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = ['id', 'cliente', 'nombre', 'cargo', 'email', 'telefono', 'es_principal', 'created_at']
        read_only_fields = ['id', 'created_at']


class ComercialMinSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.full_name
        return obj.get_full_name() or obj.username


class ClienteListSerializer(serializers.ModelSerializer):
    comercial_asignado = serializers.SerializerMethodField()
    deals_activos_count = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'nit', 'segmento', 'ciudad',
            'comercial_asignado', 'deals_activos_count', 'activo', 'created_at'
        ]

    def get_comercial_asignado(self, obj):
        if obj.comercial_asignado:
            user = obj.comercial_asignado
            full_name = ''
            if hasattr(user, 'profile'):
                full_name = user.profile.full_name
            else:
                full_name = user.get_full_name() or user.username
            return {'id': user.id, 'full_name': full_name}
        return None

    def get_deals_activos_count(self, obj):
        from apps.deals.models import ETAPAS_ACTIVAS
        return obj.deals.filter(etapa__in=ETAPAS_ACTIVAS).count()


class ClienteDetailSerializer(serializers.ModelSerializer):
    comercial_asignado = serializers.SerializerMethodField()
    contactos = ContactoSerializer(many=True, read_only=True)
    deals_activos_count = serializers.SerializerMethodField()
    deals_cerrados_count = serializers.SerializerMethodField()
    documentos_count = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = [
            'id', 'nombre', 'nit', 'segmento', 'ciudad', 'departamento',
            'direccion', 'website', 'notas', 'comercial_asignado',
            'activo', 'contactos', 'documentos_count',
            'deals_activos_count', 'deals_cerrados_count',
            'created_at', 'updated_at'
        ]

    def get_comercial_asignado(self, obj):
        if obj.comercial_asignado:
            user = obj.comercial_asignado
            full_name = ''
            if hasattr(user, 'profile'):
                full_name = user.profile.full_name
            else:
                full_name = user.get_full_name() or user.username
            return {'id': user.id, 'full_name': full_name}
        return None

    def get_deals_activos_count(self, obj):
        from apps.deals.models import ETAPAS_ACTIVAS
        return obj.deals.filter(etapa__in=ETAPAS_ACTIVAS).count()

    def get_deals_cerrados_count(self, obj):
        from apps.deals.models import ETAPAS_CERRADAS
        return obj.deals.filter(etapa__in=ETAPAS_CERRADAS).count()

    def get_documentos_count(self, obj):
        return obj.documentos.count()


class ClienteCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'nit', 'segmento', 'ciudad', 'departamento',
            'direccion', 'website', 'notas', 'comercial_asignado', 'activo'
        ]
