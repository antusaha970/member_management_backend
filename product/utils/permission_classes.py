from account.permissions import HasCustomPermission


class ProductManagementPermission(HasCustomPermission):
    required_permission = "product_management"
