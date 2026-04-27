from django.conf import settings
from django.http import HttpResponse


class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        response["Access-Control-Allow-Origin"] = settings.CORS_ALLOWED_ORIGIN
        response["Access-Control-Allow-Methods"] = settings.CORS_ALLOWED_METHODS
        response["Access-Control-Allow-Headers"] = settings.CORS_ALLOWED_HEADERS

        return response
