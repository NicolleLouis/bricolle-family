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

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "51.178.41.140", "bricolle-family.fr"]

INSTALLED_APPS = [
    "bootstrap5",
    "core.apps.CoreConfig",
    "the_bazaar",
    "baby_name",
    "agathe",
    "altered",
    'runeterra',
    "battery_simulator",
    "games_collection",
    "documents",
    "shopping_list.apps.ShoppingListConfig",
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

if ENV == "production":
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

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
