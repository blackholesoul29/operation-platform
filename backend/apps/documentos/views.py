import os
from django.http import FileResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Documento, TipoDocumento
from .serializers import DocumentoListSerializer, DocumentoCreateSerializer, TipoDocumentoSerializer


class DocumentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['cliente', 'deal', 'tipo_documento', 'estado']
    search_fields = ['nombre', 'archivo_nombre_original']
    ordering_fields = ['created_at', 'nombre', 'fecha_vencimiento']
    ordering = ['-created_at']

    def get_queryset(self):
        return Documento.objects.select_related(
            'cliente', 'deal', 'tipo_documento', 'subido_por', 'subido_por__profile'
        ).all()

    def get_serializer_class(self):
        if self.action == 'create':
            return DocumentoCreateSerializer
        return DocumentoListSerializer

    def create(self, request, *args, **kwargs):
        serializer = DocumentoCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            doc = serializer.save()
            return Response(DocumentoListSerializer(doc).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        documento = self.get_object()
        if not documento.archivo:
            return Response({'detail': 'No hay archivo adjunto.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            file_path = documento.archivo.path
            if not os.path.isfile(file_path):
                return Response({'detail': 'Archivo no encontrado en el servidor.'}, status=status.HTTP_404_NOT_FOUND)

            content_type = documento.archivo_tipo_mime or 'application/octet-stream'
            filename = documento.archivo_nombre_original or os.path.basename(file_path)

            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type,
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        documento = self.get_object()
        estado = request.data.get('estado')
        valid_states = [s[0] for s in Documento.ESTADOS]
        if not estado or estado not in valid_states:
            return Response(
                {'detail': f'Estado inválido. Opciones: {", ".join(valid_states)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        documento.estado = estado
        documento.save()
        return Response(DocumentoListSerializer(documento).data)


class TipoDocumentoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TipoDocumento.objects.all().order_by('nombre')
    serializer_class = TipoDocumentoSerializer
    search_fields = ['nombre', 'codigo']
