from django.urls import path

from .views import benchmark_view


urlpatterns = [
    path("api/django/benchmark", benchmark_view),
]
