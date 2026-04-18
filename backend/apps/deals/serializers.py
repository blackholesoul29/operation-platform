from rest_framework import serializers

from .models import Deal, DealServicio, ActividadDeal, SERVICIOS_CHOICES


class DealServicioSerializer(serializers.ModelSerializer):
    servicio_display = serializers.CharField(source='get_servicio_display', read_only=True)

    class Meta:
        model = DealServicio
        fields = ['servicio', 'servicio_display']


class ActividadDealSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    creado_por = serializers.SerializerMethodField()

    class Meta:
        model = ActividadDeal
        fields = ['id', 'tipo', 'tipo_display', 'descripcion', 'creado_por', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_creado_por(self, obj):
        if obj.creado_por:
            user = obj.creado_por
            full_name = ''
            if hasattr(user, 'profile'):
                full_name = user.profile.full_name
            else:
                full_name = user.get_full_name() or user.username
            return {'id': user.id, 'full_name': full_name}
        return None


class DealListSerializer(serializers.ModelSerializer):
    cliente = serializers.SerializerMethodField()
    etapa_display = serializers.CharField(source='get_etapa_display', read_only=True)
    servicios = serializers.SerializerMethodField()
    comercial = serializers.SerializerMethodField()
    documentos_pendientes = serializers.SerializerMethodField()
    tareas_pendientes = serializers.SerializerMethodField()
    ultima_actividad = serializers.SerializerMethodField()
    dias_en_etapa = serializers.IntegerField(read_only=True)

    class Meta:
        model = Deal
        fields = [
            'id', 'nombre', 'cliente', 'tipo_pipeline', 'origen',
            'etapa', 'etapa_display', 'servicios', 'comercial',
            'valor_estimado', 'fecha_estimada_cierre', 'probabilidad',
            'documentos_pendientes', 'tareas_pendientes', 'ultima_actividad',
            'dias_en_etapa', 'created_at',
        ]

    def get_cliente(self, obj):
        return {'id': obj.cliente.id, 'nombre': obj.cliente.nombre, 'nit': obj.cliente.nit}

    def get_servicios(self, obj):
        return list(obj.deal_servicios.values_list('servicio', flat=True))

    def get_comercial(self, obj):
        if obj.comercial:
            user = obj.comercial
            full_name = ''
            if hasattr(user, 'profile'):
                full_name = user.profile.full_name
            else:
                full_name = user.get_full_name() or user.username
            return {'id': user.id, 'full_name': full_name}
        return None

    def get_documentos_pendientes(self, obj):
        return obj.documentos.filter(estado='pendiente').count()

    def get_tareas_pendientes(self, obj):
        return obj.tareas.filter(completada=False).count()

    def get_ultima_actividad(self, obj):
        ultima = obj.actividades.first()
        if ultima:
            return ultima.created_at.date().isoformat()
        return None


class DealDetailSerializer(DealListSerializer):
    actividades = serializers.SerializerMethodField()

    class Meta(DealListSerializer.Meta):
        fields = DealListSerializer.Meta.fields + [
            'notas', 'motivo_cierre',
            'nombre_proyecto', 'tecnologia', 'capacidad_instalada_kwp',
            'generacion_estimada_mwh', 'coordenadas_lat', 'coordenadas_lng',
            'operador_red', 'volumen_recs_mwh', 'periodo_redencion',
            'registro_irec', 'etapa_changed_at', 'updated_at', 'actividades',
        ]

    def get_actividades(self, obj):
        actividades = obj.actividades.all()[:10]
        return ActividadDealSerializer(actividades, many=True).data


class DealCreateUpdateSerializer(serializers.ModelSerializer):
    servicios = serializers.ListField(
        child=serializers.ChoiceField(choices=[s[0] for s in SERVICIOS_CHOICES]),
        required=False,
        default=list,
        write_only=True
    )

    class Meta:
        model = Deal
        fields = [
            'nombre', 'cliente', 'tipo_pipeline', 'origen', 'etapa',
            'comercial', 'valor_estimado', 'fecha_estimada_cierre',
            'probabilidad', 'notas', 'motivo_cierre',
            'nombre_proyecto', 'tecnologia', 'capacidad_instalada_kwp',
            'generacion_estimada_mwh', 'coordenadas_lat', 'coordenadas_lng',
            'operador_red', 'volumen_recs_mwh', 'periodo_redencion',
            'registro_irec', 'servicios',
        ]

    def create(self, validated_data):
        servicios = validated_data.pop('servicios', [])
        deal = Deal.objects.create(**validated_data)
        for servicio in servicios:
            DealServicio.objects.get_or_create(deal=deal, servicio=servicio)
        return deal

    def update(self, instance, validated_data):
        servicios = validated_data.pop('servicios', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if servicios is not None:
            instance.deal_servicios.all().delete()
            for servicio in servicios:
                DealServicio.objects.get_or_create(deal=instance, servicio=servicio)
        return instance


class CambiarEtapaSerializer(serializers.Serializer):
    etapa_nueva = serializers.ChoiceField(choices=Deal.ETAPAS)
    motivo = serializers.CharField(required=False, allow_blank=True, default='')
    descripcion_actividad = serializers.CharField(required=False, allow_blank=True, default='')
