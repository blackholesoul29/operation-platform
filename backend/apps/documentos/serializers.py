from rest_framework import serializers

from .models import TipoDocumento, Documento


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = ['id', 'nombre', 'codigo', 'descripcion', 'tiene_vencimiento']


class DocumentoListSerializer(serializers.ModelSerializer):
    tipo_documento = serializers.SerializerMethodField()
    deal = serializers.SerializerMethodField()
    cliente = serializers.SerializerMethodField()
    subido_por = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Documento
        fields = [
            'id', 'nombre', 'tipo_documento', 'deal', 'cliente',
            'estado', 'estado_display', 'version', 'fecha_vencimiento',
            'archivo_nombre_original', 'archivo_tamanio',
            'subido_por', 'created_at',
        ]

    def get_tipo_documento(self, obj):
        if obj.tipo_documento:
            return {
                'id': obj.tipo_documento.id,
                'nombre': obj.tipo_documento.nombre,
                'codigo': obj.tipo_documento.codigo,
            }
        return None

    def get_deal(self, obj):
        if obj.deal:
            return {'id': obj.deal.id, 'nombre': obj.deal.nombre}
        return None

    def get_cliente(self, obj):
        if obj.cliente:
            return {'id': obj.cliente.id, 'nombre': obj.cliente.nombre}
        return None

    def get_subido_por(self, obj):
        if obj.subido_por:
            user = obj.subido_por
            full_name = ''
            if hasattr(user, 'profile'):
                full_name = user.profile.full_name
            else:
                full_name = user.get_full_name() or user.username
            return {'id': user.id, 'full_name': full_name}
        return None


class DocumentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = [
            'cliente', 'deal', 'tipo_documento', 'nombre',
            'descripcion', 'archivo', 'fecha_vencimiento', 'notas',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        archivo = validated_data.get('archivo')

        doc = Documento(**validated_data)
        doc.subido_por = request.user if request else None

        if archivo:
            doc.archivo_nombre_original = archivo.name
            doc.archivo_tamanio = archivo.size
            doc.archivo_tipo_mime = getattr(archivo, 'content_type', '')

        doc.save()
        return doc
