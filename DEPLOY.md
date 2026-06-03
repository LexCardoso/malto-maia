# Deploy — Malto Maia (GitHub + Render)

Fluxo: **código no GitHub (conta do Leandro) → Render (conta do projeto)** lê o
`render.yaml`, builda e sobe. Banco em **PostgreSQL** (o disco do Render free não
persiste, então SQLite perderia o cardápio editado a cada deploy).

## 1. GitHub

1. Criar um repositório (privado ou público) na conta `LexCardoso`, ex.: `malto-maia`.
2. Conectar este projeto e dar push na branch `main`:
   ```bash
   git remote add origin https://github.com/LexCardoso/malto-maia.git
   git push -u origin main
   ```

## 2. Banco PostgreSQL (escolher um)

- **Neon** (recomendado, free generoso e persistente): criar projeto em neon.tech,
  copiar a connection string (`postgres://user:pass@host/db?sslmode=require`).
- **Render Postgres**: criar no próprio Render (free por 90 dias). Copiar a *Internal
  Database URL*.

Esse valor vira a variável `DATABASE_URL`.

## 3. Render (conta do projeto)

1. **New → Blueprint** e apontar para o repositório do GitHub. O Render lê o
   `render.yaml` e cria o web service `malto-maia` (plano free, Python 3.12.10).
2. Preencher as variáveis de ambiente (as marcadas `sync:false` pedem valor):

   | Variável | Valor |
   |---|---|
   | `DATABASE_URL` | a connection string do PostgreSQL (passo 2) |
   | `ALLOWED_HOSTS` | `malto-maia.onrender.com` (+ domínio próprio, se houver) |
   | `SITE_URL` | `https://malto-maia.onrender.com` |
   | `DJANGO_SUPERUSER_USERNAME` | usuário do dono (ex.: `malto`) |
   | `DJANGO_SUPERUSER_EMAIL` | e-mail do dono |
   | `DJANGO_SUPERUSER_PASSWORD` | uma senha forte (≥10 chars) |
   | `WHATSAPP_NUMBER` | número real (formato `55DDDNUMERO`) |
   | `INSTAGRAM_HANDLE` | handle sem @ |
   | `SENTRY_DSN` | opcional (monitoramento de erros) |

   `SECRET_KEY` é gerada automaticamente pelo Render (`generateValue: true`).

3. **Deploy.** O `build.sh` roda: `pip install` → `collectstatic` → `migrate` →
   `seed_cardapio` (popula só se vazio) → cria o superusuário.

## 4. Depois do deploy

- Acessar `https://malto-maia.onrender.com/` (site) e `/painel/entrar/` (login do dono).
- Cada `git push` na `main` dispara um novo deploy automático.
- O `seed_cardapio` é idempotente: nos próximos deploys ele NÃO sobrescreve o que o
  dono editou (só popula banco vazio). Para resetar conscientemente: `seed_cardapio --force`.

## Notas

- **Free tier dorme** após ~15 min sem tráfego (primeiro acesso fica lento). Plano pago
  ou um cron de "ping" resolve, se incomodar.
- **Domínio próprio**: adicionar em Render → Settings → Custom Domains e incluir o host
  em `ALLOWED_HOSTS` + `SITE_URL`.
- **Mídia/fotos**: hoje o site usa placeholders. Se for permitir upload de fotos pelo
  painel, adicionar storage S3-compatível (ex.: Cloudflare R2) — o `prod.py` já tem o
  gancho de `STORAGES`/`default` pronto para isso.
