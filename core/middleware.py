from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve, Resolver404
from django.utils.deprecation import MiddlewareMixin


class SecurityMiddleware:
    """1) Requires login for all URLs (except login, static, admin)
       2) Prevents browser caching (fixes back-button-after-logout)"""

    EXEMPT_PREFIXES = (
        '/accounts/login/',
        '/accounts/logout/',
        '/admin/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        # Skip exempt paths
        if any(path.startswith(p) for p in self.EXEMPT_PREFIXES):
            response = self.get_response(request)
        else:
            if not request.user.is_authenticated:
                return redirect(f'{settings.LOGIN_URL}?next={path}')
            response = self.get_response(request)
        # Prevent browser caching on all pages
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class LocalOnlyLiveReload(MiddlewareMixin):
    """Inyecta el script de live reload solo cuando se navega desde localhost.

    En el servidor de despliegue (p. ej. PythonAnywhere) no se añade el script,
    evitando errores de conexión a 127.0.0.1:35729 en el navegador del cliente.
    """

    LOCAL_HOSTS = {'localhost', '127.0.0.1', '::1'}

    def process_response(self, request, response):
        host = (request.get_host() or '').split(':')[0].lower()
        if host not in self.LOCAL_HOSTS:
            return response
        from livereload.middleware import LiveReloadScript
        return LiveReloadScript(lambda req: response).process_response(request, response)
