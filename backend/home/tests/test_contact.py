import json

import pytest
from django.test import Client

from home.models import ContactSubmission, MissingModel

pytestmark = pytest.mark.django_db


class TestContactSubmitView:
    url = "/api/contact/"

    def test_valid_submission(self, client: Client):
        payload = {
            "name": "Alice",
            "email": "alice@example.com",
            "subject": "Question",
            "message": "Bonjour, je souhaite en savoir plus.",
        }
        resp = client.post(self.url, json.dumps(payload), content_type="application/json")

        assert resp.status_code == 201
        assert resp.json()["message"] == "Votre message a bien été envoyé."
        assert ContactSubmission.objects.count() == 1

        obj = ContactSubmission.objects.first()
        assert obj.name == "Alice"
        assert obj.email == "alice@example.com"
        assert obj.subject == "Question"

    def test_missing_fields_returns_400(self, client: Client):
        resp = client.post(self.url, json.dumps({}), content_type="application/json")

        assert resp.status_code == 400
        errors = resp.json()["errors"]
        assert "name" in errors
        assert "email" in errors
        assert "subject" in errors
        assert "message" in errors
        assert ContactSubmission.objects.count() == 0

    def test_partial_fields_returns_errors_for_missing_only(self, client: Client):
        payload = {"name": "Bob", "email": "bob@example.com"}
        resp = client.post(self.url, json.dumps(payload), content_type="application/json")

        assert resp.status_code == 400
        errors = resp.json()["errors"]
        assert "name" not in errors
        assert "subject" in errors
        assert "message" in errors

    def test_whitespace_only_fields_rejected(self, client: Client):
        payload = {"name": "  ", "email": "  ", "subject": "  ", "message": "  "}
        resp = client.post(self.url, json.dumps(payload), content_type="application/json")

        assert resp.status_code == 400
        assert len(resp.json()["errors"]) == 4

    def test_invalid_json(self, client: Client):
        resp = client.post(self.url, "not json", content_type="application/json")

        assert resp.status_code == 400
        assert "error" in resp.json()

    def test_get_not_allowed(self, client: Client):
        resp = client.get(self.url)
        assert resp.status_code == 405


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
