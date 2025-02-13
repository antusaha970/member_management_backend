
from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"
    rate = "60/min"

    def get_cache_key(self, request, view):
        return f"throttle_{self.scope}_{self.get_ident(request)}"
