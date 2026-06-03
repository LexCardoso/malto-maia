"""Paginas publicas do cardapio."""
import io

import segno
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

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


def menu_qr(request):
    """QR Code (SVG) que aponta para o cardapio online — pra imprimir nas mesas."""
    url = request.build_absolute_uri(reverse("cardapio:menu"))
    qr = segno.make(url, error="m")
    buff = io.BytesIO()
    qr.save(buff, kind="svg", scale=6, border=2, dark="#3B2A20", light="#ffffff")
    resp = HttpResponse(buff.getvalue(), content_type="image/svg+xml")
    resp["Cache-Control"] = "public, max-age=3600"
    return resp
