---
name: maltomaia-security
description: |
  Postura de segurança: acesso ao painel (login staff + django-axes anti-bruteforce),
  hardening de produção (HSTS, cookies Secure, SSL redirect, CSRF trusted origins) e
  zero segredo hardcoded. Use ao mexer em settings, login do painel, views protegidas,
  ou qualquer coisa que toque autenticação/segredos.
---

# maltomaia-security

Site público + um painel privado onde o dono edita o cardápio. A superfície de risco
é pequena, mas o painel precisa ser sólido: ninguém além do staff entra.

## Acesso ao painel

- Login em `/painel/entrar/` (`PainelLoginView`, template branded). `LOGIN_URL` aponta pra lá.
- Toda view do painel usa `@staff_required` (`user_passes_test(is_active and is_staff)`).
  Anônimo → redirect pro login. **Nunca** uma view de edição sem esse decorator.
- Ações que mudam estado (toggle, excluir, marcar data) são `@require_POST` + CSRF.
- **django-axes**: 5 tentativas → bloqueio 1h (`AXES_*` no base.py), backend `AxesStandaloneBackend`
  PRIMEIRO, middleware `AxesMiddleware` por ÚLTIMO. Em dev, `AXES_ENABLED = False`.
- `/django-admin/` (admin nativo) existe como ferramenta de poder — mesmo gate de staff.

## Hardening de produção (`settings/prod.py`)

`DEBUG=False`, HSTS 1 ano (+subdomains, preload), `SECURE_SSL_REDIRECT`, cookies
`Secure`+`HttpOnly`+`SameSite=Lax`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS=DENY`,
`CSRF_TRUSTED_ORIGINS` derivado de `ALLOWED_HOSTS`, `SECURE_PROXY_SSL_HEADER` (Render).

## Segredos

Tudo via `env(...)` (`django-environ`, lê `.env.defaults` → `.env.local`). `SECRET_KEY`
em prod vem do Render (`generateValue`). **Nunca** literal no código. Senha do admin
via `DJANGO_SUPERUSER_PASSWORD` (env), nunca no repo.

## Quando disparar

- Mexer em `settings/base.py` ou `settings/prod.py`.
- Mexer no login do painel, em `@staff_required`, ou adicionar view ao painel.
- Adicionar ação que muda estado (garantir POST + CSRF + staff).
- Qualquer coisa com senha, token, chave, segredo.

## Anti-patterns

- ❌ View de edição no painel sem `@staff_required`.
- ❌ Ação destrutiva via GET (tem que ser POST + CSRF).
- ❌ Segredo literal no código em vez de `env(...)`.
- ❌ Afrouxar `ALLOWED_HOSTS` (ex.: `["*"]`) ou desligar axes em produção.
- ❌ `DEBUG=True` vazando pra prod.

## Referências

- `maltomaia/settings/base.py` (axes, validators), `settings/prod.py` (hardening).
- `painel/views.py` (`staff_required`, `PainelLoginView`), `templates/painel/lockout.html`.
- Skills irmãs: `maltomaia-deploy`, `maltomaia-validation`.
