"""Root URLconf — Malto Maia."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("painel/", include("painel.urls")),
    path("cardapio/", include("cardapio.urls")),
    path("encomenda/", include("pedidos.urls")),
    path("", include("core.urls")),
]
