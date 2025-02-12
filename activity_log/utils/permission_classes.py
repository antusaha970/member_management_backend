
from account.permissions import HasCustomPermission


class AllUserActivityLogPermission(HasCustomPermission):
    required_permission = "all_user_activity_log"
