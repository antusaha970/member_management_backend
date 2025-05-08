from account.permissions import HasCustomPermission


class RegisterUserPermission(HasCustomPermission):
    required_permission = "/reg"


class GroupCreatePermission(HasCustomPermission):
    required_permission = "group_create"


class GroupEditPermission(HasCustomPermission):
    required_permission = "group_edit"


class GroupViewPermission(HasCustomPermission):
    required_permission = "/groups"


class GroupDeletePermission(HasCustomPermission):
    required_permission = "group_delete"


class GroupUserManagementPermission(HasCustomPermission):
    required_permission = "group_management"


class CustomPermissionSetPermission(HasCustomPermission):
    required_permission = "/permissions"
