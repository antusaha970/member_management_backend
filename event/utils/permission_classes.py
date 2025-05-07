from account.permissions import HasCustomPermission


class EventManagementPermission(HasCustomPermission):
    required_permission = "event_management"
