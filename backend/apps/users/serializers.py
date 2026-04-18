from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'is_active']


class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_active = serializers.BooleanField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active']

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return 'comercial'


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False, default='')
    last_name = serializers.CharField(max_length=150, required=False, default='')
    role = serializers.ChoiceField(choices=UserProfile.ROLES, default='comercial')
    phone = serializers.CharField(max_length=20, required=False, default='')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre de usuario.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'comercial')
        phone = validated_data.pop('phone', '')
        password = validated_data.pop('password')

        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(password)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.phone = phone
        profile.save()

        return user


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(choices=UserProfile.ROLES, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        phone = validated_data.pop('phone', None)

        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if role is not None:
            profile.role = role
        if phone is not None:
            profile.phone = phone
        profile.save()

        return instance


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError("Se requieren usuario y contraseña.")

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Credenciales inválidas.")
        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo.")

        refresh = RefreshToken.for_user(user)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        user_data = UserProfileSerializer(profile).data

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas nuevas no coinciden.")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
