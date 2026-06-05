from django.urls import path

from . import views

app_name = "cardapio"

urlpatterns = [
    path("", views.menu, name="menu"),
    path("pdf/", views.menu_pdf, name="menu_pdf"),
    path("qr/", views.menu_qr, name="menu_qr"),
    path("item/<int:pk>/foto/", views.item_foto, name="item_foto"),
]
