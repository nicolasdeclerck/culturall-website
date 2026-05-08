"""POC HTMX — tests pour la page À propos rendue côté serveur.

Cf. docs/poc-htmx-a-propos.md.
"""

import pytest
from django.test import Client
from django.urls import reverse

from pages.models import StaticContentPage

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


class TestStaticPageHtmlView:
    def test_renders_seeded_a_propos_page(self, client):
        response = client.get(reverse("static-page-html"))

        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/html")
        assert b"<title>" in response.content
        assert "À propos" in response.content.decode()

    def test_renders_body_as_html(self, client):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.body = "<p>Bonjour <strong>monde</strong></p>"
        page.save()

        response = client.get(reverse("static-page-html"))
        body = response.content.decode()

        assert "<strong>monde</strong>" in body

    def test_includes_header_and_footer(self, client):
        response = client.get(reverse("static-page-html"))
        body = response.content.decode()

        assert 'class="header"' in body
        assert "Nos Projets" in body
        assert "Mentions légales" in body
        assert 'class="site-footer"' in body

    def test_returns_404_when_page_unpublished(self, client):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.unpublish()

        response = client.get(reverse("static-page-html"))
        assert response.status_code == 404

    def test_only_get_allowed(self, client):
        response = client.post(reverse("static-page-html"))
        assert response.status_code == 405

    def test_loads_static_assets(self, client):
        response = client.get(reverse("static-page-html"))
        body = response.content.decode()

        assert "/static/css/main.css" in body
        assert "/static/js/site.js" in body
