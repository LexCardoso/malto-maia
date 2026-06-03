"""Tela de encomenda — carrinho client-side que finaliza no WhatsApp."""
from django.shortcuts import render

from cardapio.services import menu_localizado


def encomenda(request):
    lang = getattr(request, "LANG", "pt")
    return render(
        request,
        "pedidos/encomenda.html",
        {"categorias": menu_localizado(lang, apenas_disponiveis=True)},
    )
