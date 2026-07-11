import threading

_audit_thread = threading.local()


def get_audit_user():
    return getattr(_audit_thread, 'user', None)


def get_audit_ip():
    return getattr(_audit_thread, 'ip', None)


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _audit_thread.user = request.user if request.user.is_authenticated else None
        _audit_thread.ip = request.META.get('REMOTE_ADDR')
        _audit_thread.before_stack = []
        try:
            response = self.get_response(request)
        finally:
            _audit_thread.user = None
            _audit_thread.ip = None
            _audit_thread.before_stack = []
        return response
