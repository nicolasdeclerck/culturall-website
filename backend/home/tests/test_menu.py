"""Menu principal administrable via l'arbre de pages Wagtail.

Le header construit son menu à partir des enfants live de la HomePage cochés
« Show in menus » (`show_in_menus`), via le template tag `get_site_root`.
Ces tests vérifient le rendu et le pilotage du menu depuis l'admin (case à
cocher + publication), sur les pages seedées par la migration `0010`.
"""

import pytest
from django.test import Client
from wagtail.models import Page

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


# Lien tel que rendu dans le menu : `@click="close()"` est propre au header,
# ce qui distingue ces ancres des autres liens de la page (cartes projets…).
def _menu_link(title):
    return f'@click="close()">{title}</a>'


class TestMainMenu:
    def test_renders_seeded_menu_in_order(self, client):
        body = client.get("/").content.decode()

        for title in ("Projets", "À propos", "Contact"):
            assert _menu_link(title) in body

        # Ordre attendu : Projets, À propos, Contact (ordre de l'arbre).
        assert (
            body.index(_menu_link("Projets"))
            < body.index(_menu_link("À propos"))
            < body.index(_menu_link("Contact"))
        )

    def test_uses_native_page_urls(self, client):
        body = client.get("/").content.decode()

        assert f'href="/projets/" {_menu_link("Projets")}' in body
        assert f'href="/a-propos/" {_menu_link("À propos")}' in body
        assert f'href="/contact/" {_menu_link("Contact")}' in body

    def test_page_excluded_when_show_in_menus_unchecked(self, client):
        Page.objects.filter(slug="a-propos").update(show_in_menus=False)

        body = client.get("/").content.decode()

        assert _menu_link("À propos") not in body
        # Les autres entrées restent présentes.
        assert _menu_link("Projets") in body
        assert _menu_link("Contact") in body

    def test_unpublished_page_excluded(self, client):
        Page.objects.get(slug="contact").specific.unpublish()

        body = client.get("/").content.decode()

        assert _menu_link("Contact") not in body
        assert _menu_link("Projets") in body
