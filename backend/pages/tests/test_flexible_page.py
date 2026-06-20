"""Page flexible (StreamField) rendue côté serveur via le template Wagtail natif.

Gabarit « passe-partout » utilisé quand le design n'est pas encore figé :
l'éditeur empile des blocs (titre, texte riche, image, cartes, bouton, vidéo)
dans le StreamField `body`, rendus par les templates de `home/blocks/`.
"""

import pytest
from django.test import Client

from home.models import HomePage
from pages.models import FlexiblePage

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def flexible_page():
    """Crée une FlexiblePage publiée comme enfant direct de la HomePage."""
    home = HomePage.objects.first()
    page = FlexiblePage(
        title="Page flexible",
        slug="page-flexible",
        body=[
            ("heading", {"text": "Mon titre flexible"}),
            ("paragraph", "<p>Un peu de <strong>contenu</strong>.</p>"),
        ],
    )
    home.add_child(instance=page)
    page.save_revision().publish()
    return page


class TestFlexiblePageModel:
    def test_parent_is_home_page(self, flexible_page):
        home = HomePage.objects.first()
        assert flexible_page.get_parent().specific == home

    def test_allowed_under_home_only(self):
        assert FlexiblePage.parent_page_types == ["home.HomePage"]
        assert FlexiblePage.subpage_types == []


class TestFlexiblePageRendering:
    def test_renders_title_and_blocks(self, client, flexible_page):
        response = client.get("/page-flexible/")

        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/html")
        body = response.content.decode()
        assert "Page flexible" in body
        assert "Mon titre flexible" in body
        assert "<strong>contenu</strong>" in body
        # Le wrapper stylé est réutilisé pour bénéficier du CSS existant.
        assert "custom-section__inner" in body

    def test_includes_header_and_footer(self, client, flexible_page):
        body = client.get("/page-flexible/").content.decode()

        assert 'class="header"' in body
        assert 'class="site-footer"' in body

    def test_empty_body_renders_without_section(self, client):
        home = HomePage.objects.first()
        page = FlexiblePage(title="Vide", slug="vide")
        home.add_child(instance=page)
        page.save_revision().publish()

        body = client.get("/vide/").content.decode()
        assert "Vide" in body
        assert "custom-section__inner" not in body

    def test_returns_404_when_unpublished(self, client, flexible_page):
        flexible_page.unpublish()
        assert client.get("/page-flexible/").status_code == 404
