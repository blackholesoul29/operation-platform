from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notificacion
from .serializers import NotificacionSerializer


class NotificacionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificacionSerializer
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).select_related('deal', 'cliente')

    @action(detail=True, methods=['patch'], url_path='leer')
    def leer(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response(NotificacionSerializer(notificacion).data)

    @action(detail=False, methods=['post'], url_path='leer-todas')
    def leer_todas(self, request):
        updated = Notificacion.objects.filter(
            usuario=request.user, leida=False
        ).update(leida=True)
        return Response({'detail': f'{updated} notificaciones marcadas como leídas.'})

    @action(detail=False, methods=['get'], url_path='count')
    def count(self, request):
        qs = Notificacion.objects.filter(usuario=request.user)
        total = qs.count()
        no_leidas = qs.filter(leida=False).count()
        return Response({'total': total, 'no_leidas': no_leidas})
