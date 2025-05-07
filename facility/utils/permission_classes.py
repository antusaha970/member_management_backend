from account.permissions import HasCustomPermission


class FacilityManagementPermission(HasCustomPermission):
    required_permission = "facility_management"
