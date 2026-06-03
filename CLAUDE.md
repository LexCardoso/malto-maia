# Malto Maia — Contexto do Projeto (para o Claude Code)

Site de uma cafeteria/doceria (Praia Seca, Araruama – RJ): landing page + cardápio +
encomenda, mais um painel onde o dono (não-técnico) loga e edita o cardápio. **Single-tenant**
(uma única casa — não há multi-tenant/isolamento por cliente). Mobile-first e bilíngue PT/EN.

## Stack

- Django 5.0, Python 3.12.10. SQLite em dev, PostgreSQL (Neon/Render) em prod.
- Templates Django + CSS próprio (design system em `static/css/malto.css`, veio do Claude Design).
- WhiteNoise (estático), Gunicorn, deploy no Render via `render.yaml` + `build.sh`.
- django-axes (anti-bruteforce no login), Sentry opcional. CI: GitHub Actions.

## Estrutura

```
maltomaia/settings/   base.py | dev.py (SQLite, DEBUG) | prod.py (Postgres, hardening)
core/                 landing, i18n (core/i18n.py STRINGS), middleware LANG, set_language, health
cardapio/             models (Categoria, Item, ConfiguracaoSite), services (leitura localizada),
                      admin, seed_cardapio (idempotente), menu público
pedidos/              encomenda (carrinho client-side -> WhatsApp, static/js/order.js)
painel/               PainelLoginView + @staff_required CRUD do cardápio
templates/            base.html (público) | painel/base_painel.html (admin)
```

## Convenções (regras em vigor)

- **PT-BR** é o idioma de trabalho e padrão do site; EN é o segundo idioma do toggle.
- **Bilíngue sempre**: string de UI em `core/i18n.py` (`{% t "chave" %}`), com `pt` E `en`.
  Conteúdo de cardápio em campos `*_pt`/`*_en`. Nada novo entra só em um idioma.
- **Preço `None` = "a definir"** — nunca renderizar `R$ 0,00`. Filtro `brl` formata `R$ 1.234,56`.
- **Leitura de cardápio via `cardapio/services.py`** (já localizado + otimizado).
- **Seed idempotente**: `seed_cardapio` só popula banco vazio (não sobrescreve edições).
- **Painel só staff**: toda view de edição com `@staff_required`; ação de estado com `@require_POST`.
- **Produção = PostgreSQL** (Render free não persiste SQLite). `DATABASE_URL` manda.
- **Sem emoji** em código/commits salvo se já for convenção do arquivo.

## Settings

- `manage.py` usa `maltomaia.settings.dev` por padrão. `wsgi.py`/Render usam `.prod`.
- Variáveis via `django-environ`: lê `.env.defaults` (commitado) e depois `.env.local`.

## Roteador de skills (USE NO INÍCIO DE TAREFA NOVA)

Antes de propor solução, classifique a tarefa:
```bash
python scripts/dev/skill_router.py classify "<descrição>" --paths <arquivo>
```
Leia as SKILL.md do top-K e aplique. Skills: `maltomaia-skill-router` (meta),
`maltomaia-cardapio`, `maltomaia-i18n`, `maltomaia-templates`, `maltomaia-deploy`,
`maltomaia-security`, `maltomaia-validation`, `maltomaia-memory-keeper`. Se o router não
achar skill (score < 0.10): PARE e reporte (ver regra do "sem skill" na skill-router).

Guardião read-only antes de release: `python scripts/dev/monitor.py`.

## Validação antes de commit

`manage.py check` → `makemigrations --check` → `manage.py test` → (estático? `collectstatic`
prod) → smoke. Use o venv: `venv\Scripts\python.exe`. Ver skill `maltomaia-validation`.

## Estado atual

Infra + esqueleto funcionais (landing, cardápio do banco, encomenda, painel de edição,
skill router, monitor, CI). **Pendente**: integrar o layout final do design (pixel),
fotos reais (hoje placeholders `.ph`), QR code do cardápio, mapa real na seção Visite.
