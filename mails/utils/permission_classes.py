from account.permissions import HasCustomPermission



class BulkEmailManagementPermission(HasCustomPermission):
    required_permission = "bulk_emails_management"