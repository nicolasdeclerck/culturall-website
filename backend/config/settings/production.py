"""Settings de production — Gunicorn + WhiteNoise + MinIO/S3."""

import os

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE

DEBUG = False

# WhiteNoise sert /static/ directement depuis Django (cf. note dans
# docker/django/Dockerfile : Traefik ne sert pas les statics).
MIDDLEWARE = [
    MIDDLEWARE[0],  # SecurityMiddleware en premier
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]

# Storage : statics via WhiteNoise (compressed manifest), médias via S3/MinIO.
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.environ.get("MINIO_BUCKET_NAME", "media"),
            "endpoint_url": os.environ.get("MINIO_ENDPOINT_URL"),
            "access_key": os.environ.get("MINIO_ROOT_USER"),
            "secret_key": os.environ.get("MINIO_ROOT_PASSWORD"),
            "default_acl": "public-read",
            "querystring_auth": False,
            "url_protocol": "https:",
            "custom_domain": (
                os.environ.get("MINIO_PUBLIC_URL", "")
                .replace("https://", "")
                .replace("http://", "")
                + "/"
                + os.environ.get("MINIO_BUCKET_NAME", "media")
            ),
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Sécurité
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
