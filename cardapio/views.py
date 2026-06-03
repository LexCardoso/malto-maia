"""Paginas publicas do cardapio."""
from django.shortcuts import render

from .models import ConfiguracaoSite
from .services import menu_localizado


def menu(request):
    lang = getattr(request, "LANG", "pt")
    config = ConfiguracaoSite.get()
    return render(
        request,
        "cardapio/menu.html",
        {
            "categorias": menu_localizado(lang),
            "atualizado_em": config.cardapio_atualizado_em,
            "modo_impressao": request.GET.get("print") == "1",
        },
    )
