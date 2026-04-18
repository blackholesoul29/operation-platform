from rest_framework.permissions import BasePermission

ROLE_HIERARCHY = {
    'comercial': 1,
    'operativo': 2,
    'legal': 2,
    'manager_comercial': 3,
    'admin': 4,
}


def get_user_role(user):
    if hasattr(user, 'profile'):
        return user.profile.role
    return 'comercial'


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and get_user_role(request.user) == 'admin'


class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and ROLE_HIERARCHY.get(get_user_role(request.user), 0) >= 3
        )


class IsComercialOrAbove(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and ROLE_HIERARCHY.get(get_user_role(request.user), 0) >= 1
        )
