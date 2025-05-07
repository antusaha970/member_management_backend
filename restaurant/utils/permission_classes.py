from account.permissions import HasCustomPermission


class RestaurantManagementPermission(HasCustomPermission):
    required_permission = "restaurant_management"
