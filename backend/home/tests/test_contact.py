import pytest
from django.test import Client, override_settings

from home import turnstile as turnstile_module
from home.models import ContactSubmission
from home.turnstile import verify_turnstile

pytestmark = pytest.mark.django_db


class TestContactPageView:
    """Page de contact rendue côté serveur (Django + HTMX)."""

    url = "/contact/"
    HTMX = {"HTTP_HX_REQUEST": "true"}

    valid_payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "subject": "Question",
        "message": "Bonjour, je souhaite en savoir plus.",
    }

    def test_get_renders_form(self, client: Client):
        resp = client.get(self.url)

        assert resp.status_code == 200
        body = resp.content.decode()
        assert 'class="contact-form"' in body
        assert 'hx-post="/contact/"' in body
        assert "csrfmiddlewaretoken" in body

    def test_htmx_valid_post_creates_submission_and_returns_success(self, client: Client):
        resp = client.post(self.url, self.valid_payload, **self.HTMX)

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "contact-success" in body
        assert "bien été envoyé" in body
        # Le partial succès ne contient plus le formulaire
        assert 'class="contact-form"' not in body

        assert ContactSubmission.objects.count() == 1
        obj = ContactSubmission.objects.first()
        assert obj.name == "Alice"
        assert obj.email == "alice@example.com"
        assert obj.subject == "Question"

    def test_htmx_invalid_post_returns_form_with_errors(self, client: Client):
        resp = client.post(self.url, {}, **self.HTMX)

        assert resp.status_code == 200
        body = resp.content.decode()
        assert 'class="contact-form"' in body
        assert "Le nom est requis." in body
        # L'apostrophe est échappée par Django (&#x27;) → on teste une sous-chaîne
        assert "email est requis." in body
        assert "Le sujet est requis." in body
        assert "Le message est requis." in body
        assert ContactSubmission.objects.count() == 0

    def test_htmx_whitespace_only_rejected(self, client: Client):
        payload = {"name": "  ", "email": "  ", "subject": "  ", "message": "  "}
        resp = client.post(self.url, payload, **self.HTMX)

        assert resp.status_code == 200
        assert "contact-success" not in resp.content.decode()
        assert ContactSubmission.objects.count() == 0

    def test_non_htmx_valid_post_renders_full_page_with_success(self, client: Client):
        resp = client.post(self.url, self.valid_payload)

        assert resp.status_code == 200
        body = resp.content.decode()
        # Page complète (header) + message de succès
        assert 'class="header"' in body
        assert "contact-success" in body
        assert ContactSubmission.objects.count() == 1

    def test_invalid_email_rejected(self, client: Client):
        payload = {**self.valid_payload, "email": "pas-un-email"}
        resp = client.post(self.url, payload, **self.HTMX)

        assert resp.status_code == 200
        assert "email valide" in resp.content.decode()
        assert ContactSubmission.objects.count() == 0

    def test_put_not_allowed(self, client: Client):
        resp = client.put(self.url)
        assert resp.status_code == 405

    def test_head_allowed(self, client: Client):
        assert client.head(self.url).status_code == 200


class TestContactTurnstile:
    """Protection anti-bots Cloudflare Turnstile du formulaire de contact."""

    url = "/contact/"
    HTMX = {"HTTP_HX_REQUEST": "true"}

    valid_payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "subject": "Question",
        "message": "Bonjour, je souhaite en savoir plus.",
    }

    def test_widget_absent_when_site_key_not_configured(self, client: Client):
        # En dev/tests la clé n'est pas configurée → pas de widget.
        body = client.get(self.url).content.decode()
        assert "cf-turnstile" not in body

    @override_settings(TURNSTILE_SITE_KEY="1x00000000000000000000AA")
    def test_widget_rendered_when_site_key_configured(self, client: Client):
        body = client.get(self.url).content.decode()
        assert "cf-turnstile" in body
        assert "1x00000000000000000000AA" in body
        assert "challenges.cloudflare.com" in body

    @override_settings(TURNSTILE_SECRET_KEY="secret")
    def test_post_rejected_when_verification_fails(self, client: Client, monkeypatch):
        monkeypatch.setattr("home.views.verify_turnstile", lambda *a, **k: False)
        resp = client.post(self.url, self.valid_payload, **self.HTMX)

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "anti-robot" in body
        assert 'class="contact-form"' in body
        assert ContactSubmission.objects.count() == 0

    @override_settings(TURNSTILE_SECRET_KEY="secret")
    def test_post_accepted_when_verification_succeeds(self, client: Client, monkeypatch):
        monkeypatch.setattr("home.views.verify_turnstile", lambda *a, **k: True)
        resp = client.post(self.url, self.valid_payload, **self.HTMX)

        assert resp.status_code == 200
        assert "contact-success" in resp.content.decode()
        assert ContactSubmission.objects.count() == 1


class TestVerifyTurnstileHelper:
    """Logique de court-circuit du helper (aucun appel réseau)."""

    @override_settings(TURNSTILE_SECRET_KEY="")
    def test_disabled_when_secret_absent(self):
        # Sans clé secrète, la vérification est désactivée (toujours True).
        assert verify_turnstile("") is True
        assert verify_turnstile("n-importe-quoi") is True

    @override_settings(TURNSTILE_SECRET_KEY="secret")
    def test_empty_token_fails_without_network(self, monkeypatch):
        # Un jeton vide échoue immédiatement, sans toucher au réseau.
        def _boom(*a, **k):  # pragma: no cover - ne doit jamais être appelé
            raise AssertionError("urlopen ne doit pas être appelé pour un jeton vide")

        monkeypatch.setattr(turnstile_module.request, "urlopen", _boom)
        assert verify_turnstile("") is False


class TestContactSubmissionModel:
    def test_str(self, db):
        obj = ContactSubmission.objects.create(
            name="Alice", email="a@b.com", subject="Test", message="Hello"
        )
        assert "Test" in str(obj)
        assert "Alice" in str(obj)

    def test_ordering(self, db):
        ContactSubmission.objects.create(
            name="First", email="a@b.com", subject="S1", message="M1"
        )
        ContactSubmission.objects.create(
            name="Second", email="a@b.com", subject="S2", message="M2"
        )
        first = ContactSubmission.objects.first()
        assert first.name == "Second"
