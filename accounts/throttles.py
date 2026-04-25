from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, SimpleRateThrottle


class LoginThrottle(AnonRateThrottle):
    scope = "login"

class RegisterThrottle(AnonRateThrottle):
    scope = "register"


#added but not used yet
class IPThrottle(SimpleRateThrottle):
    scope = "ip"

    def get_cache_key(self, request, view):
        # Get client IP
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            ip = xff.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")

        return self.cache_format % {
            "scope": self.scope,
            "ident": ip
        }