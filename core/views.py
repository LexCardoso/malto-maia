"""Landing page, troca de idioma e endpoints utilitarios."""
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from cardapio.models import ConfiguracaoSite
from cardapio.services import destaques_localizados


def landing(request):
    lang = getattr(request, "LANG", "pt")
    config = ConfiguracaoSite.get()
    return render(
        request,
        "core/landing.html",
        {
            "destaques": destaques_localizados(lang, limite=4),
            "atualizado_em": config.cardapio_atualizado_em,
        },
    )


def set_language(request, lang):
    if lang in settings.LANGS:
        request.session["lang"] = lang
    nxt = request.GET.get("next") or request.META.get("HTTP_REFERER")
    if nxt and url_has_allowed_host_and_scheme(
        nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(nxt)
    return redirect("core:landing")


def health(request):
    """Health check do Render — devolve o commit no ar (RENDER_GIT_COMMIT)."""
    import os

    commit = os.environ.get("RENDER_GIT_COMMIT", "dev")[:7]
    return HttpResponse(f"ok {commit}", content_type="text/plain")


def robots(request):
    body = "User-agent: *\nAllow: /\nDisallow: /painel/\nDisallow: /django-admin/\n"
    return HttpResponse(body, content_type="text/plain")
