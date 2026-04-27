from django.urls import include, path
from django.http import HttpResponse


urlpatterns = [
    path("ping", lambda request: HttpResponse("pong\n", content_type="text/plain; charset=utf-8")),
    path("", include("benchmark_api.urls")),
]
