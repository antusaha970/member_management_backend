from account.permissions import HasCustomPermission
# Auth Views form Authorization

class MemberManagementPermission(HasCustomPermission):
    required_permission = "member_management"
