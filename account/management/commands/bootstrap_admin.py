from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from account.models import PermissonModel, GroupModel, AssignGroupPermission


class Command(BaseCommand):
    help = 'Creates initial admin and other model data'

    def handle(self, *args, **kwargs):
        self.create_admin_with_groups()

    def create_admin_with_groups(self):
        try:
            User = get_user_model()
            if not User.objects.filter(username="admin").exists():
                user = User.objects.create_superuser(
                    username="admin",
                    email="admin@example123.com",
                    password="admin"
                )
            else:
                user = User.objects.get(username="admin")
            all_permission_name = ["group_view", "group_delete", "group_create", "group_edit", "register_account", "group_management", "all_activity_log",
                                   "restaurant_management", "member_financial_management", "add_member", "view_member", "update_member", "delete_member"]
            permissions = []
            for permission_name in all_permission_name:
                if PermissonModel.objects.filter(name=permission_name).exists():
                    permission = PermissonModel.objects.get(
                        name=permission_name)
                    permissions.append(permission)
                else:
                    permission = PermissonModel.objects.create(
                        name=permission_name)
                    permissions.append(permission)

            group, _ = GroupModel.objects.get_or_create(name="super_admin")
            group.permission.set(permissions)

            if not AssignGroupPermission.objects.filter(user=user, group=group).exists():
                assigned_group = AssignGroupPermission.objects.create(
                    user=user)
                assigned_group.group.add(group)
                assigned_group.save()

            self.stdout.write(self.style.SUCCESS(
                "Admin user created with super admin group."))
        except Exception as e:
            self.stdout.write(
                "something went wrong", str(e))
