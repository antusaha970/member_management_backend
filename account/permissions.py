from rest_framework.permissions import BasePermission
from .models import AssignGroupPermission, GroupModel, PermissonModel
import pdb
from django.core.cache import cache


class HasCustomPermission(BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        if not request.user or request.user.is_anonymous:
            return False

        if self.required_permission is None:
            return False
        user = request.user
        cache_key = f"user_permissions_{user.id}"
        user_permissions = cache.get(cache_key)
        if user_permissions is None:
            print("Database hit for checking permissions..")
            all_user_groups = AssignGroupPermission.objects.filter(
                user=user).prefetch_related("group__permission")
            user_permissions = set()

            for assign_group in all_user_groups:
                for group in assign_group.group.all():
                    for perm in group.permission.all():
                        user_permissions.add(perm.name)

            print("Caching user permissions...")
            cache.set(cache_key, list(user_permissions),
                      timeout=60*5)  # 5 minutes

        return self.required_permission in user_permissions
