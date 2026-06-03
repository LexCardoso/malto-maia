from django.urls import path

from . import views

app_name = "cardapio"

urlpatterns = [
    path("", views.menu, name="menu"),
    path("qr/", views.menu_qr, name="menu_qr"),
]
