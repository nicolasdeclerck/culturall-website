"""Settings de développement local."""

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Désactive le manifest staticfiles en dev pour éviter les erreurs sur les
# assets non collectés.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Le backend email est résolu dans base.py : backend console tant que
# EMAIL_HOST n'est pas renseigné (cas par défaut en dev), SMTP sinon. Pour
# tester un vrai serveur mail en local, renseigner EMAIL_* dans .env.dev.
