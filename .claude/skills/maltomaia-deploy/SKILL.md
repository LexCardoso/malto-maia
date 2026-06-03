---
name: maltomaia-deploy
description: |
  Deploy no Render via GitHub: render.yaml, build.sh, Procfile, gunicorn, WhiteNoise,
  PostgreSQL (Neon/Render), collectstatic, migrate, seed e createsuperuser. Use ao
  mexer em infra de deploy, requirements, settings de prod, ou ao subir/promover release.
---

# maltomaia-deploy

Stack de deploy: **GitHub (repo do Leandro) → Render (conta do projeto)**, Python
3.12.10, Gunicorn, WhiteNoise (estático), PostgreSQL em produção, SQLite em dev.

## Peças

- `render.yaml` — blueprint do web service (free plan). `buildCommand: bash build.sh`,
  `startCommand: gunicorn maltomaia.wsgi`. Env vars: `SECRET_KEY` (generateValue),
  `DATABASE_URL`/`ALLOWED_HOSTS`/`SITE_URL` (sync:false), `DJANGO_SUPERUSER_*` (sync:false).
- `build.sh` — roda a cada deploy: `pip install` → `collectstatic` → `migrate` →
  `seed_cardapio` (idempotente) → `createsuperuser` se as env vars existirem. **LF only**
  (`.gitattributes` força).
- `requirements.txt` — Django, gunicorn, whitenoise, psycopg2-binary, django-environ,
  django-axes, sentry-sdk. `runtime.txt`/`.python-version` = 3.12.10.
- `maltomaia/settings/prod.py` — Postgres (`env.db`, sslmode require), WhiteNoise
  `CompressedManifestStaticFilesStorage`, Sentry opcional, hardening HTTPS.

## Banco (decisão importante)

Render free **não tem disco persistente** → SQLite seria zerado a cada redeploy. Como
o dono **edita o cardápio em produção**, o banco TEM que ser PostgreSQL persistente
(Neon free ou Render Postgres). `DATABASE_URL` controla isso; nunca apontar prod pra SQLite.

## Fluxo de release

1. Validar local (`maltomaia-validation`): check + makemigrations --check + test + smoke.
2. Commit + push na branch conectada ao Render → deploy automático roda `build.sh`.
3. Conferir logs do Render; `migrate` e `seed` não podem falhar (build aborta com errexit).
4. Estático mudou? WhiteNoise + ManifestStorage versionam por hash — só precisa do
   `collectstatic` (já no build). Sem cache manual.

## Variáveis de ambiente (Render)

`SECRET_KEY` (auto), `DATABASE_URL` (Postgres), `ALLOWED_HOSTS` (host .onrender.com +
domínio), `SITE_URL`, `WHATSAPP_NUMBER`, `INSTAGRAM_HANDLE`, `SENTRY_DSN` (opcional),
`DJANGO_SUPERUSER_USERNAME/EMAIL/PASSWORD` (cria o admin no 1º deploy).

## Quando disparar

- Mexer em `render.yaml`, `build.sh`, `Procfile`, `requirements*.txt`, `runtime.txt`.
- Mexer em `settings/prod.py` ou variáveis de ambiente.
- Promover release / investigar build quebrado no Render.

## Anti-patterns

- ❌ Apontar produção pra SQLite (perde os dados a cada deploy).
- ❌ `build.sh` com CRLF (Render não executa) — manter LF.
- ❌ `seed_cardapio` não-idempotente (sobrescreveria edições do dono).
- ❌ Commitar `.env.local`/segredo (só `.env.defaults` é commitado, com valores de dev).
- ❌ Esquecer `ALLOWED_HOSTS` → 400 em produção; `DATABASE_URL` → build quebra no migrate.

## Referências

- `render.yaml`, `build.sh`, `Procfile`, `requirements.txt`, `maltomaia/settings/prod.py`.
- Skills irmãs: `maltomaia-security` (hardening), `maltomaia-validation` (pré-deploy).
