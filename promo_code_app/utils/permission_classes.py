from account.permissions import HasCustomPermission


class PromoCodeManagementPermission(HasCustomPermission):
    required_permission = "promo_code_management"
