from django.conf import settings
from django.http import HttpResponse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if settings.MAINTENANCE_MODE and self.allow_on_header(request.headers):
            return HttpResponse("site is in maintanence mode", status=503, headers={
                'content-type': 'application/json'
            })

        response = self.get_response(request)

        return response

    def allow_on_header(self, headers={}):
        if not 'allow-maintenance' in headers:
            return True
        return headers['allow-maintenance'] != settings.MAINTENANCE_BYPASS_PASSWORD
