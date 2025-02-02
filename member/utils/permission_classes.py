from account.permissions import HasCustomPermission
# Auth Views form Authorization


class ViewMemberPermission(HasCustomPermission):
    required_permission = "view_member"


class DeleteMemberPermission(HasCustomPermission):
    required_permission = "delete_member"


class AddMemberPermission(HasCustomPermission):
    required_permission = "add_member"


class UpdateMemberPermission(HasCustomPermission):
    required_permission = "update_member"
