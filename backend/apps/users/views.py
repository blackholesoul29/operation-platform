from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .permissions import IsAdmin, get_user_role
from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Stateless JWT — client discards token
        return Response({'detail': 'Sesión cerrada correctamente.'}, status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('profile').all().order_by('username')
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [IsAdmin()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        role = get_user_role(user)
        if role == 'admin':
            return User.objects.select_related('profile').all().order_by('username')
        # Non-admin can only see their own user or all active users in list
        return User.objects.select_related('profile').filter(is_active=True).order_by('username')

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            return Response(UserProfileSerializer(profile).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.update(instance, serializer.validated_data)
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            return Response(UserProfileSerializer(profile).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        user = self.get_object()
        # Only admin or the user themselves can change password
        if request.user != user and get_user_role(request.user) != 'admin':
            return Response(
                {'detail': 'No tiene permiso para cambiar esta contraseña.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': 'Contraseña actualizada correctamente.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
