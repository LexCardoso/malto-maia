"""Define request.LANG (pt/en) a partir da sessao."""
from django.conf import settings


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.session.get("lang")
        if lang not in settings.LANGS:
            lang = settings.LANG_DEFAULT
        request.LANG = lang
        return self.get_response(request)
