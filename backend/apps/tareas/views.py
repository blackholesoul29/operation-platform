from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Tarea
from .serializers import TareaListSerializer, TareaCreateUpdateSerializer
from apps.users.permissions import get_user_role, ROLE_HIERARCHY


class TareaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['deal', 'cliente', 'completada', 'prioridad', 'asignado_a']
    search_fields = ['titulo']
    ordering_fields = ['fecha_limite', 'prioridad', 'created_at']
    ordering = ['completada', 'fecha_limite']

    def get_queryset(self):
        user = self.request.user
        role = get_user_role(user)
        qs = Tarea.objects.select_related(
            'deal', 'cliente',
            'asignado_a', 'asignado_a__profile',
            'creado_por', 'creado_por__profile'
        )
        if ROLE_HIERARCHY.get(role, 0) < 3:
            qs = qs.filter(Q(asignado_a=user) | Q(creado_por=user))
        return qs

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TareaCreateUpdateSerializer
        return TareaListSerializer

    def create(self, request, *args, **kwargs):
        serializer = TareaCreateUpdateSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            tarea = serializer.save()
            return Response(TareaListSerializer(tarea).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = TareaCreateUpdateSerializer(
            instance, data=request.data, partial=partial, context={'request': request}
        )
        if serializer.is_valid():
            tarea = serializer.save()
            return Response(TareaListSerializer(tarea).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='completar')
    def completar(self, request, pk=None):
        tarea = self.get_object()
        tarea.completada = True
        tarea.fecha_completada = timezone.now()
        tarea.save()

        # Create activity on deal if linked
        if tarea.deal:
            from apps.deals.models import ActividadDeal
            ActividadDeal.objects.create(
                deal=tarea.deal,
                tipo='tarea',
                descripcion=f"Tarea completada: {tarea.titulo}",
                creado_por=request.user,
            )

        return Response(TareaListSerializer(tarea).data)
