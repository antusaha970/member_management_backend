from account.permissions import HasCustomPermission


class RegisterUserPermission(HasCustomPermission):
    required_permission = "register_account"
