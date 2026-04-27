from rest_framework import permissions


class IsStaffWithAdminRole(permissions.BasePermission):
    """
    staff-пользователи с ролью 0.0 (суперадмин) или 1.0 (админ), либо is_superuser.
    """

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        return bool(u.is_staff and u.is_active and u.role in (0.0, 1.0))
