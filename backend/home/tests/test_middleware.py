import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


class TestLoginRequiredMiddleware:
    def test_blocks_unauthenticated_when_enabled(self, client: Client, site_settings):
        site_settings.require_authentication = True
        site_settings.save()

        resp = client.get("/api/projects/")
        assert resp.status_code == 401
        assert resp.json()["error"] == "Authentification requise."

    def test_allows_unauthenticated_when_disabled(self, client: Client, site_settings):
        site_settings.require_authentication = False
        site_settings.save()

        resp = client.get("/api/projects/")
        assert resp.status_code == 200

    def test_allows_authenticated_when_enabled(self, client: Client, user, site_settings):
        site_settings.require_authentication = True
        site_settings.save()

        client.force_login(user)
        resp = client.get("/api/projects/")
        assert resp.status_code == 200

    @pytest.mark.parametrize("path", [
        "/admin/",
        "/django-admin/",
        "/api/auth/check/",
        "/api/auth/login/",
        "/static/test.css",
        "/media/test.jpg",
    ])
    def test_excluded_paths_always_allowed(self, client: Client, site_settings, path):
        site_settings.require_authentication = True
        site_settings.save()

        resp = client.get(path)
        assert resp.status_code != 401
