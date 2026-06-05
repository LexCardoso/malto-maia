"""Paginas publicas do cardapio."""
import io

import segno
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import http_date

from .models import ConfiguracaoSite, FotoSite, Item
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


def menu_pdf(request):
    """Pagina dedicada de impressao do cardapio — charme da marca, pronta pra PDF.

    Autossuficiente (estilo inline) e so com itens disponiveis, pra um impresso limpo.
    """
    lang = getattr(request, "LANG", "pt")
    config = ConfiguracaoSite.get()
    return render(
        request,
        "cardapio/menu_pdf.html",
        {
            "categorias": menu_localizado(lang, apenas_disponiveis=True),
            "atualizado_em": config.cardapio_atualizado_em,
        },
    )


def item_foto(request, pk):
    """Serve a foto do produto guardada no banco (bytes). Publica (aparece no site)."""
    item = (
        Item.objects.filter(pk=pk)
        .only("foto", "foto_mime", "atualizado_em")
        .first()
    )
    if not item or not item.foto:
        raise Http404("item sem foto")
    resp = HttpResponse(bytes(item.foto), content_type=item.foto_mime or "image/jpeg")
    resp["Cache-Control"] = "public, max-age=86400"
    if item.atualizado_em:
        resp["Last-Modified"] = http_date(item.atualizado_em.timestamp())
    return resp


def foto_site(request, slug):
    """Serve uma foto do site (hero, galeria, etc.) guardada no banco. Publica."""
    fs = (
        FotoSite.objects.filter(slug=slug)
        .only("foto", "foto_mime", "atualizado_em")
        .first()
    )
    if not fs or not fs.foto:
        raise Http404("foto do site nao encontrada")
    resp = HttpResponse(bytes(fs.foto), content_type=fs.foto_mime or "image/jpeg")
    resp["Cache-Control"] = "public, max-age=86400"
    if fs.atualizado_em:
        resp["Last-Modified"] = http_date(fs.atualizado_em.timestamp())
    return resp


def menu_qr(request):
    """QR Code (SVG) que aponta para o cardapio online — pra imprimir nas mesas."""
    url = request.build_absolute_uri(reverse("cardapio:menu"))
    qr = segno.make(url, error="m")
    buff = io.BytesIO()
    qr.save(buff, kind="svg", scale=6, border=2, dark="#3B2A20", light="#ffffff")
    resp = HttpResponse(buff.getvalue(), content_type="image/svg+xml")
    resp["Cache-Control"] = "public, max-age=3600"
    return resp
