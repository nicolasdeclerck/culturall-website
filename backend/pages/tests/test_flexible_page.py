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
        # Le titre garde sa section ; seule la section de contenu est absente.
        assert '<section class="custom-section"' not in body

    def test_returns_404_when_unpublished(self, client, flexible_page):
        flexible_page.unpublish()
        assert client.get("/page-flexible/").status_code == 404


class TestInteractiveListBlock:
    @pytest.fixture
    def page_with_list(self):
        home = HomePage.objects.first()
        page = FlexiblePage(
            title="Liste",
            slug="liste",
            body=[
                (
                    "interactive_list",
                    {
                        "items": [
                            {
                                "title": "Item A",
                                "subtitle": "Sous-titre A",
                                "content": "<p>Détail <strong>A</strong></p>",
                            },
                            {
                                "title": "Item B",
                                "subtitle": "Sous-titre B",
                                "content": "<p>Détail B</p>",
                            },
                        ]
                    },
                )
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        return page

    def test_renders_titles_subtitles_and_rich_content(self, client, page_with_list):
        body = client.get("/liste/").content.decode()

        # Titres (volet gauche) et sous-titres (volet droit + inline mobile).
        assert "Item A" in body
        assert "Item B" in body
        assert "Sous-titre A" in body
        # Le texte riche est bien rendu en HTML.
        assert "<strong>A</strong>" in body

    def test_titles_are_h3_and_subtitles_h4(self, client, page_with_list):
        body = client.get("/liste/").content.decode()

        assert '<h3 class="ilist__title">Item A' in body
        assert '<h4 class="ilist__subtitle-inline">Sous-titre A</h4>' in body
        assert '<h4 class="ilist__panel-subtitle">Sous-titre A</h4>' in body

    def test_first_item_active_by_default_for_no_js(self, client, page_with_list):
        body = client.get("/liste/").content.decode()

        # État actif rendu côté serveur sur le 1er item (fallback sans JS) et
        # câblage Alpine présent pour l'interaction au survol.
        assert "ilist__trigger--active" in body
        assert "ilist__panel--active" in body
        assert 'x-data="{ active: 0 }"' in body
        assert "@mouseenter" in body

    def test_item_without_link_is_not_a_link(self, client, page_with_list):
        body = client.get("/liste/").content.decode()
        # Sans lien : item non cliquable (pas de classe ni d'ancre dédiée).
        assert "ilist__trigger--link" not in body
        assert '<div class="ilist__trigger' in body

    def test_item_with_link_renders_anchor_to_page(self, client):
        from pages.models import StaticContentPage

        target = StaticContentPage.objects.get(slug="a-propos")
        home = HomePage.objects.first()
        page = FlexiblePage(
            title="Liste liée",
            slug="liste-liee",
            body=[
                (
                    "interactive_list",
                    {
                        "items": [
                            {"title": "Vers À propos", "link_page": target},
                        ]
                    },
                )
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        body = client.get("/liste-liee/").content.decode()
        assert "ilist__trigger--link" in body
        assert 'href="/a-propos/"' in body
