"""Contexto global de template: idioma + dados de contato do site."""
from django.conf import settings

from cardapio.models import ConfiguracaoSite


def site_context(request):
    lang = getattr(request, "LANG", settings.LANG_DEFAULT)
    config = ConfiguracaoSite.get()
    whatsapp = (config.whatsapp or settings.WHATSAPP_NUMBER).strip()
    instagram = (config.instagram or settings.INSTAGRAM_HANDLE).strip().lstrip("@")
    return {
        "LANG": lang,
        "OTHER_LANG": "en" if lang == "pt" else "pt",
        "WHATSAPP_NUMBER": whatsapp,
        "INSTAGRAM_HANDLE": instagram,
        "SITE_URL": settings.SITE_URL,
    }
