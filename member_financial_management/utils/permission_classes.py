from account.permissions import HasCustomPermission


class MemberFinancialManagementPermission(HasCustomPermission):
    required_permission = "member_financial_management"
