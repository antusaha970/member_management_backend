from rest_framework.permissions import BasePermission
from .models import AssignGroupPermission

class HasCustomPermission(BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        
        if self.required_permission is None:
            return False
        access_view= AssignGroupPermission.objects.filter(
            user=request.user,
            group__permission__name=self.required_permission
        ).exists()
        if access_view:
            return True
        else:
            return False