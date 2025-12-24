import dj_database_url
import os
from pathlib import Path
from decouple import config

from django.conf.global_settings import STORAGES

BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure a default SECRET_KEY is set for environments where it might not be (e.g., testing)
# Try to load from environment, but if not found or is None, use a dummy key.
SECRET_KEY = config("SECRET_KEY", default=None)
if not SECRET_KEY:
    SECRET_KEY = "dummy_secret_key_for_testing_do_not_use_in_production"

DEBUG = config("DEBUG", default=True)
ENV = config("ENV", default="local")
IS_PRODUCTION = str(ENV).lower() == "production"
FLASH_CARDS_MCP_TOKEN = config("FLASH_CARDS_MCP_TOKEN", default="")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "51.178.41.140",
    "bricolle-family.fr",
    "www.bricolle-family.fr",
]

INSTALLED_APPS = [
    "bootstrap5",
    "core.apps.CoreConfig",
    "the_bazaar",
    "baby_name",
    "agathe",
    "altered",
    'runeterra',
    "finance_simulator",
    "games_collection",
    "flash_cards",
    "civilization7",
    "documents",
    "capitalism.apps.CapitalismConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
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
    "bricolle_family.middleware.login_required_middleware.LoginRequiredMiddleware",
    "bricolle_family.middleware.admin_required_middleware.AdminRequiredMiddleware",
]

ROOT_URLCONF = "bricolle_family.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "bricolle_family", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bricolle_family.wsgi.application"

if IS_PRODUCTION:
    DATABASES = {
        "default": dj_database_url.config(
            default=config("DATABASE_URL"), conn_max_age=600
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_TZ = False

CSRF_TRUSTED_ORIGINS = [
    "https://bricolle-family.fr",
    "https://www.bricolle-family.fr",
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = IS_PRODUCTION
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365 if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = IS_PRODUCTION
SECURE_HSTS_PRELOAD = IS_PRODUCTION
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = BASE_DIR / "staticfiles"

if IS_PRODUCTION:
    STORAGES["staticfiles"] = {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
else:
    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_EXEMPT_URLS = [
    "flash_cards:api_question_create",
    "flash_cards:api_categories",
    "flash_cards:home",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "[{levelname}] {asctime} {name}: {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
            },
            "django.request": {
                "handlers": ["console"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.server": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
