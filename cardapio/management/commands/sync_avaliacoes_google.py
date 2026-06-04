"""Sincroniza avaliacoes do Google (Places API) como rascunho no painel.

Uso:  python manage.py sync_avaliacoes_google
Requer settings GOOGLE_PLACES_API_KEY e GOOGLE_PLACE_ID (via env).
Idempotente: re-rodar nao duplica nem mexe na curadoria (campo 'aparece').
"""
from django.core.management.base import BaseCommand, CommandError

from cardapio.reviews_google import GoogleReviewsError, sincronizar_google


class Command(BaseCommand):
    help = "Puxa as avaliacoes do Google (ate ~5) e salva como rascunho no painel."

    def handle(self, *args, **options):
        try:
            r = sincronizar_google()
        except GoogleReviewsError as e:
            raise CommandError(str(e))
        self.stdout.write(
            self.style.SUCCESS(
                f"Google: {r['encontradas']} lidas, {r['criadas']} novas (rascunho), "
                f"{r['atualizadas']} atualizadas."
            )
        )
