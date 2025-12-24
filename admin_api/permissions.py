from rest_framework.permissions import BasePermission
from users.choices import UserRole

class IsAdmin(BasePermission):
    def has_permission(self,request,view):
        return(
            request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
            and request.user.is_active
        )