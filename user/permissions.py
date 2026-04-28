from rest_framework import permissions


def can_assign_to_user(actor, target) -> bool:
    if not actor or not actor.is_authenticated:
        return False
    if actor.is_superuser:
        return True
    return actor.is_admin_role()


class IsStaffWithAdminRole(permissions.BasePermission):
    """
    staff-пользователи с глобальной ролью superadmin/admin, либо is_superuser.
    """

    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if u.is_superuser:
            return True
        return bool(u.is_staff and u.is_active and u.is_admin_role())
