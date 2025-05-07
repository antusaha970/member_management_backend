from account.permissions import HasCustomPermission
# Auth Views form Authorization


class ViewMemberPermission(HasCustomPermission):
    required_permission = "members/view"


class DeleteMemberPermission(HasCustomPermission):
    required_permission = "delete_member"


class AddMemberPermission(HasCustomPermission):
    required_permission = "members/add"


class UpdateMemberPermission(HasCustomPermission):
    required_permission = "update_member"
