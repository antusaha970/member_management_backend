from rest_framework.permissions import BasePermission
from .models import AssignGroupPermission, GroupModel, PermissonModel
import pdb
from django.core.cache import cache


# class HasCustomPermission(BasePermission):
#     required_permission = None

#     def has_permission(self, request, view):

#         if self.required_permission is None:
#             return False

#         user = request.user
#         all_user_groups = AssignGroupPermission.objects.filter(
#             user=user).prefetch_related("group__permission")
#         user_permissions = set()

#         for assign_group in all_user_groups:
#             for group in assign_group.group.all():
#                 for perm in group.permission.all():
#                     user_permissions.add(perm.name)
#         all_user_groups = AssignGroupPermission.objects.filter(user=user)

#         # Check if the required permission exists in the cached permissions
#         return self.required_permission in user_permissions

#         # access_view= AssignGroupPermission.objects.filter(
#         #     user=request.user
#         #     # group__permission__name=self.required_permission
#         # )
#         # access_view = AssignGroupPermission.objects.filter(user=request.user)
#         # user_groups = GroupModel.objects.filter(group__user=request.user)
#         # group_permissions = PermissonModel.objects.filter(group__in=user_groups)
#         # permission_names = group_permissions.values_list("name", flat=True)
#         # print(permission_names)
#         # for permission in permission_names:
#         #     print(permission)
#         #     if self.required_permission==permission:
#         #         return True

#         # return False

#         # queryset = AssignGroupPermission.objects.filter(user=request.user)
#         # queryset = queryset.filter(group__isnull=False)  #
#         # queryset = queryset.filter(group__permission__isnull=False)
#         # queryset = queryset.filter(group__permission__name=self.required_permission)
#         # access_view = queryset.exists()

#         # pdb.set_trace()
#         # group=access_view

#         # print(group)

#         # if access_view:
#         #     return True
#         # else:
#         #     return False

#         # access_view= AssignGroupPermission.objects.filter(user=request.user)
#         # pdb.set_trace()
#         # group=access_view.group.objects.all()

#         # for gro in group:
#         #     for per in gro:
#         #         for name in per:
#         #             if name== self.required_permission:
#         #                 return True
#         #             else:
#         #                 return False


class HasCustomPermission(BasePermission):
    required_permission = None

    def has_permission(self, request, view):
        if self.required_permission is None:
            return False

        user = request.user
        cache_key = f"user_permissions_{user.id}"

        user_permissions = cache.get(cache_key)

        if user_permissions is None:
            all_user_groups = AssignGroupPermission.objects.filter(
                user=user).prefetch_related("group__permission")
            user_permissions = set()

            for assign_group in all_user_groups:
                for group in assign_group.group.all():
                    for perm in group.permission.all():
                        user_permissions.add(perm.name)

            cache.set(cache_key, user_permissions, timeout=600)

        return self.required_permission in user_permissions
