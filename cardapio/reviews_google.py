"""Sincronizacao de avaliacoes do Google -> modelo Avaliacao.

Usa a Places API (New): GET v1/places/{place_id} com FieldMask 'reviews'. O Google
expoe ate ~5 avaliacoes (escolhidas por ele) — nao da pra puxar todas por aqui.

Estrategia: salvar como RASCUNHO (aparece=False); o dono liga no painel quais aparecem.
Idempotente por (fonte='google', ref=id-da-avaliacao-no-google) -> re-sincronizar NAO
duplica e NAO mexe no que ja foi curado (so atualiza autor/texto/nota).

Config (via env / settings): GOOGLE_PLACES_API_KEY e GOOGLE_PLACE_ID. Sem isso, fica
desligado (o painel esconde o botao e o command/endpoint avisam).

Sem dependencia externa: usa urllib da stdlib.
"""
import json
import urllib.error
import urllib.request

from django.conf import settings

PLACES_ENDPOINT = "https://places.googleapis.com/v1/places/{place_id}"
FIELD_MASK = "id,rating,userRatingCount,reviews"


class GoogleReviewsError(Exception):
    """Falha esperada ao falar com o Google (config faltando, HTTP, conexao)."""


def esta_configurado():
    return bool(
        getattr(settings, "GOOGLE_PLACES_API_KEY", "")
        and getattr(settings, "GOOGLE_PLACE_ID", "")
    )


def buscar_avaliacoes_google(api_key=None, place_id=None, timeout=15):
    """GET na Places API (New). Devolve o JSON cru (dict) ou levanta GoogleReviewsError."""
    api_key = api_key or getattr(settings, "GOOGLE_PLACES_API_KEY", "")
    place_id = place_id or getattr(settings, "GOOGLE_PLACE_ID", "")
    if not api_key or not place_id:
        raise GoogleReviewsError("Faltam GOOGLE_PLACES_API_KEY e/ou GOOGLE_PLACE_ID.")

    req = urllib.request.Request(
        PLACES_ENDPOINT.format(place_id=place_id),
        headers={
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", "replace")[:400]
        raise GoogleReviewsError(f"HTTP {e.code} do Google: {corpo}")
    except urllib.error.URLError as e:
        raise GoogleReviewsError(f"Falha de conexao com o Google: {e.reason}")
    except (ValueError, json.JSONDecodeError) as e:
        raise GoogleReviewsError(f"Resposta invalida do Google: {e}")


def extrair_avaliacoes(data):
    """JSON da Places API -> lista de dicts {ref, autor, texto, nota}. Funcao pura (testavel)."""
    avaliacoes = []
    for r in (data or {}).get("reviews", []):
        ref = (r.get("name") or "").strip()
        texto = (
            (r.get("text") or {}).get("text")
            or (r.get("originalText") or {}).get("text")
            or ""
        ).strip()
        autor = ((r.get("authorAttribution") or {}).get("displayName") or "").strip()
        if not (ref and texto and autor):
            continue
        try:
            nota = int(round(float(r.get("rating") or 0)))
        except (TypeError, ValueError):
            nota = 5
        avaliacoes.append(
            {"ref": ref, "autor": autor[:80], "texto": texto, "nota": max(1, min(5, nota))}
        )
    return avaliacoes


def salvar_avaliacoes(avaliacoes):
    """Upsert por (fonte='google', ref). Cria como rascunho; preserva 'aparece'/'ordem'.

    Logica explicita (sem update_or_create): no update so mexe em autor/texto/nota, entao
    o que o dono ja curou (aparece) e a ordem nunca sao tocados ao re-sincronizar.
    """
    from .models import Avaliacao

    criadas = atualizadas = 0
    for a in avaliacoes:
        if not a["ref"]:
            continue
        obj = Avaliacao.objects.filter(fonte="google", ref=a["ref"]).first()
        if obj is None:
            Avaliacao.objects.create(
                fonte="google", ref=a["ref"], autor=a["autor"],
                texto=a["texto"], nota=a["nota"], aparece=False, ordem=0,
            )
            criadas += 1
        else:
            obj.autor, obj.texto, obj.nota = a["autor"], a["texto"], a["nota"]
            obj.save(update_fields=["autor", "texto", "nota"])
            atualizadas += 1
    return {"criadas": criadas, "atualizadas": atualizadas}


def sincronizar_google():
    """Pipeline: busca -> extrai -> salva. Devolve resumo. Levanta GoogleReviewsError."""
    data = buscar_avaliacoes_google()
    avaliacoes = extrair_avaliacoes(data)
    resumo = salvar_avaliacoes(avaliacoes)
    resumo["encontradas"] = len(avaliacoes)
    return resumo
