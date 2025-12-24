from rest_framework.permissions import BasePermission
from users.choices import UserRole


class IsClient(BasePermission):
    def has_persmission(self,request,view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.CLIENT
        )