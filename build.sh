#!/usr/bin/env bash
# Build script do Render — roda a cada deploy (push na branch conectada).
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput --settings=maltomaia.settings.prod
python manage.py migrate --settings=maltomaia.settings.prod

# Popula o cardapio APENAS se o banco estiver vazio (nao sobrescreve edicoes do admin).
python manage.py seed_cardapio --settings=maltomaia.settings.prod

# Cria superusuario se as env vars existirem e ele ainda nao existir (idempotente).
if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser --noinput --settings=maltomaia.settings.prod || true
fi
