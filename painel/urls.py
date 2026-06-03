from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "painel"

urlpatterns = [
    path("entrar/", views.PainelLoginView.as_view(), name="login"),
    path("sair/", LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("item/novo/", views.item_novo, name="item_novo"),
    path("item/<int:pk>/editar/", views.item_editar, name="item_editar"),
    path("item/<int:pk>/disponibilidade/", views.item_toggle, name="item_toggle"),
    path("item/<int:pk>/excluir/", views.item_excluir, name="item_excluir"),
    path("atualizar-data/", views.marcar_atualizado, name="marcar_atualizado"),
]
