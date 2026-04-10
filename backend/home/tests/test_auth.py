import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


class TestAuthCheck:
    url = "/api/auth/check/"

    def test_anonymous_user(self, client: Client, site_settings):
        resp = client.get(self.url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is False
        assert "require_authentication" in data

    def test_authenticated_user(self, client: Client, user, site_settings):
        client.force_login(user)
        resp = client.get(self.url)
        assert resp.status_code == 200
        assert resp.json()["authenticated"] is True

    def test_reflects_site_setting(self, client: Client, site_settings):
        site_settings.require_authentication = False
        site_settings.save()

        resp = client.get(self.url)
        assert resp.json()["require_authentication"] is False


class TestAuthLogin:
    url = "/api/auth/login/"

    def test_valid_credentials(self, client: Client, user):
        payload = {"username": "testuser", "password": "Testpass123!"}
        resp = client.post(self.url, json.dumps(payload), content_type="application/json")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Connexion réussie."

    def test_invalid_credentials(self, client: Client, user):
        payload = {"username": "testuser", "password": "wrong"}
        resp = client.post(self.url, json.dumps(payload), content_type="application/json")
        assert resp.status_code == 401

    def test_missing_fields(self, client: Client):
        resp = client.post(self.url, json.dumps({}), content_type="application/json")
        assert resp.status_code == 400

    def test_invalid_json(self, client: Client):
        resp = client.post(self.url, "bad", content_type="application/json")
        assert resp.status_code == 400

    def test_get_not_allowed(self, client: Client):
        resp = client.get(self.url)
        assert resp.status_code == 405


class TestAuthLogout:
    url = "/api/auth/logout/"

    def test_logout(self, client: Client, user):
        client.force_login(user)
        resp = client.post(self.url, content_type="application/json")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Déconnexion réussie."

        # Verify session is cleared
        check = client.get("/api/auth/check/")
        assert check.json()["authenticated"] is False

    def test_get_not_allowed(self, client: Client):
        resp = client.get(self.url)
        assert resp.status_code == 405
