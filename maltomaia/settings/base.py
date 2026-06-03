"""Shared settings for all environments — Malto Maia."""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# .env.defaults (commitado) e depois .env.local (gitignored, sobrescreve).
env_defaults = BASE_DIR / ".env.defaults"
if env_defaults.exists():
    env.read_env(str(env_defaults))

env_local = BASE_DIR / ".env.local"
if env_local.exists():
    env.read_env(str(env_local), overwrite=True)

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
SITE_URL = env("SITE_URL", default="http://localhost:8000")

# Contato / encomendas
WHATSAPP_NUMBER = env("WHATSAPP_NUMBER", default="5521999999999")
INSTAGRAM_HANDLE = env("INSTAGRAM_HANDLE", default="maltomaia")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "axes",
    # project apps
    "core",
    "cardapio",
    "pedidos",
    "painel",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # define request.LANG (pt/en) a partir de sessao/?lang=
    "core.middleware.LanguageMiddleware",
    # axes deve ficar por ULTIMO para capturar tentativas de login
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# django-axes: anti-bruteforce no login do painel
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hora de bloqueio
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "painel/lockout.html"

ROOT_URLCONF = "maltomaia.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "maltomaia.wsgi.application"
ASGI_APPLICATION = "maltomaia.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Toggle PT/EN proprio da UI (nao usa o i18n de .po do Django; ver core/i18n.py)
LANGS = ["pt", "en"]
LANG_DEFAULT = "pt"

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/painel/entrar/"
LOGIN_REDIRECT_URL = "/painel/"
LOGOUT_REDIRECT_URL = "/"
