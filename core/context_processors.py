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
        "TRIPADVISOR_URL": config.tripadvisor_url,
        # String com ponto decimal (nao localizar: URL do Google Maps exige ponto,
        # senao o locale pt-BR formata com virgula e o mapa quebra).
        "MAP_LAT": str(config.latitude) if config.latitude is not None else "",
        "MAP_LNG": str(config.longitude) if config.longitude is not None else "",
        "TEM_MAPA": config.tem_mapa,
    }
