# Malto Maia — Doceria & Cafeteria

Site (landing + cardápio + encomenda) e painel de administração da **Doceria &
Cafeteria Malto Maia**, em Praia Seca, Araruama – RJ. O dono loga no painel e edita
o cardápio que aparece no site.

## Stack

- **Backend:** Django 5.0 / Python 3.12
- **Frontend:** Templates Django + CSS próprio (design system em `static/css/malto.css`)
- **Banco:** SQLite (dev) / PostgreSQL (prod — Neon ou Render Postgres)
- **Hosting:** Render (free tier) via `render.yaml`
- **Estático:** WhiteNoise (manifest + compressão)
- **CI:** GitHub Actions (`.github/workflows/test.yml`)
- **Idiomas:** PT-BR (padrão) / EN, toggle próprio no header

## Setup local

```bash
git clone https://github.com/LexCardoso/<repo>.git
cd <repo>

python -m venv venv
venv\Scripts\activate                 # Windows
# source venv/bin/activate            # Linux/Mac
pip install -r requirements-dev.txt

copy .env.local.example .env.local    # opcional (dev usa .env.defaults)

python manage.py migrate
python manage.py seed_cardapio         # popula o cardápio (idempotente)
python manage.py createsuperuser       # cria o login do painel
python manage.py runserver
```

Acessos: site em `/`, cardápio em `/cardapio/`, encomenda em `/encomenda/`,
painel em `/painel/` (login em `/painel/entrar/`).

## Estrutura

```
maltomaia/            # Projeto Django (settings/, urls, wsgi)
  settings/           # base.py, dev.py, prod.py
core/                 # Landing, i18n (PT/EN), troca de idioma, health
cardapio/             # Categoria, Item, ConfiguracaoSite + seed + menu público
pedidos/              # Encomenda (carrinho client-side -> WhatsApp)
painel/               # Painel do dono (login staff + edição do cardápio)
templates/            # base.html + páginas + painel/
static/               # css/ (malto, site, painel, responsive), img/ (logos), js/
scripts/dev/          # skill_router.py + monitor.py (ferramentas de dev)
.claude/              # skills/ + agents/ (roteador de skills, guardião)
```

## Cardápio

- `python manage.py seed_cardapio` popula 11 categorias / ~86 itens (idempotente —
  só roda em banco vazio; `--force` recria). Os dados espelham o design.
- Preço vazio = **"a definir"**. `destaque` = carro-chefe (aparece na landing).
  `disponivel` controla se sai no cardápio/encomenda.

## Deploy (Render)

`git push` na branch conectada → Render roda `build.sh` (pip install, collectstatic,
migrate, seed, createsuperuser). Variáveis necessárias no Render: `DATABASE_URL`
(PostgreSQL), `ALLOWED_HOSTS`, `SITE_URL`, `DJANGO_SUPERUSER_*`. Detalhes em `DEPLOY.md`.

## Ferramentas de dev (`.claude/` + `scripts/dev/`)

- **skill_router** — roteia a tarefa pra skill certa: `python scripts/dev/skill_router.py classify "..."`.
- **monitor** — vigia read-only (acesso ao painel, segredos, migrations, i18n):
  `python scripts/dev/monitor.py`.

## Ambientes

| Arquivo | Propósito |
|---------|-----------|
| `.env.defaults` | Valores padrão de dev (commitado) |
| `.env.local` | Overrides locais (gitignored) |
| `.env.local.example` | Template |
