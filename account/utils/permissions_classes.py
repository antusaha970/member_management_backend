from account.permissions import HasCustomPermission


class RegisterUserPermission(HasCustomPermission):
    required_permission = "register_account"


class GroupCreatePermission(HasCustomPermission):
    required_permission = "group_create"


class GroupEditPermission(HasCustomPermission):
    required_permission = "group_edit"


class GroupViewPermission(HasCustomPermission):
    required_permission = "group_view"


class GroupDeletePermission(HasCustomPermission):
    required_permission = "group_delete"


class GroupUserManagementPermission(HasCustomPermission):
    required_permission = "group_user_management"
