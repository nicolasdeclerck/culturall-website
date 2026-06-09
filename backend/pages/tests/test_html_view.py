"""Pages statiques rendues côté serveur via le template Wagtail natif.

Phase 1 de la migration monolithe Wagtail : généralise le rendu serveur
(initialement limité au POC /a-propos/) à toutes les StaticContentPage.
"""

import pytest
from django.test import Client
from django.urls import reverse

from pages.models import StaticContentPage

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


def url(slug):
    return reverse("static-page-html", kwargs={"slug": slug})


class TestStaticPageServerRendering:
    @pytest.mark.parametrize(
        "slug, title",
        [
            ("a-propos", "À propos"),
            ("mentions-legales", "Mentions légales"),
        ],
    )
    def test_renders_seeded_pages(self, client, slug, title):
        response = client.get(url(slug))

        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/html")
        body = response.content.decode()
        assert "<title>" in body
        assert title in body

    def test_renders_body_as_html(self, client):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.body = "<p>Bonjour <strong>monde</strong></p>"
        page.save()

        body = client.get(url("a-propos")).content.decode()
        assert "<strong>monde</strong>" in body

    def test_includes_header_and_footer(self, client):
        body = client.get(url("a-propos")).content.decode()

        assert 'class="header"' in body
        assert "Nos Projets" in body
        assert "Mentions légales" in body
        assert 'class="site-footer"' in body

    def test_loads_static_assets(self, client):
        body = client.get(url("a-propos")).content.decode()

        assert "/static/css/main.css" in body
        assert "/static/js/site.js" in body

    def test_returns_404_when_page_unpublished(self, client):
        page = StaticContentPage.objects.get(slug="mentions-legales")
        page.unpublish()

        assert client.get(url("mentions-legales")).status_code == 404

    def test_returns_404_for_unknown_slug(self, client):
        assert client.get(url("slug-inexistant")).status_code == 404

    def test_only_get_allowed(self, client):
        assert client.post(url("a-propos")).status_code == 405

    def test_head_request_allowed(self, client):
        assert client.head(url("a-propos")).status_code == 200

    def test_native_preview_renders_template(self):
        """La preview Wagtail native rend le template page statique (plus de headless)."""
        page = StaticContentPage.objects.get(slug="a-propos")
        page.body = "<p>Brouillon aperçu</p>"

        response = page.make_preview_request()

        assert response.status_code == 200
        body = response.content.decode()
        assert "Brouillon aperçu" in body
        assert "static-page-wrapper" in body
