
from account.permissions import HasCustomPermission


class AllUserActivityLogPermission(HasCustomPermission):
    required_permission = "activity_log_management"
