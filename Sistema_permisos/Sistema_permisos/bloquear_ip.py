from django.http import HttpResponseForbidden

BLOQUEAR_IPS = ['10.10.10.67']  # IPs a bloquear
MODULOS_BLOQUEADOS = ['/Modulo_admin/']  # Rutas a proteger

class BloquearIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_cliente = self.get_client_ip(request)
        path = request.path

        if any(path.startswith(modulo) for modulo in MODULOS_BLOQUEADOS):
            if ip_cliente in BLOQUEAR_IPS:
                return HttpResponseForbidden("Acceso denegado desde esta IP.")

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')