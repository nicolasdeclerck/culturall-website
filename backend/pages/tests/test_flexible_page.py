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


class TestHostedVideoBlock:
    """Bloc « Vidéo hébergée » : fichier téléversé (wagtailmedia) lu via le
    lecteur HTML5 natif, à distinguer de l'embed YouTube/Vimeo."""

    @pytest.fixture
    def page_with_video(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from wagtailmedia.models import get_media_model

        media = get_media_model().objects.create(
            title="Clip de démo",
            file=SimpleUploadedFile(
                "clip-demo.mp4", b"\x00\x00\x00\x18ftypmp42", content_type="video/mp4"
            ),
            type="video",
        )
        home = HomePage.objects.first()
        page = FlexiblePage(
            title="Vidéo hébergée",
            slug="video-hebergee",
            body=[("hosted_video", {"video": media, "caption": "Notre dernière vidéo"})],
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        return page

    def test_renders_native_html5_player(self, client, page_with_video):
        body = client.get("/video-hebergee/").content.decode()

        # Lecteur natif (pas d'iframe tierce) avec une <source> typée.
        assert 'class="custom-section__video-player"' in body
        assert "<video" in body
        assert "controls" in body
        assert 'type="video/mp4"' in body
        assert "clip-demo" in body

    def test_renders_caption(self, client, page_with_video):
        body = client.get("/video-hebergee/").content.decode()
        assert "Notre dernière vidéo" in body

    def test_uses_video_dimensions_when_available(self, client):
        """Quand la largeur/hauteur sont renseignées, elles sont reportées sur
        la balise <video> pour que le bloc épouse le ratio de la vidéo."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        from wagtailmedia.models import get_media_model

        media = get_media_model().objects.create(
            title="Vidéo dimensionnée",
            file=SimpleUploadedFile(
                "dim.mp4", b"\x00\x00\x00\x18ftypmp42", content_type="video/mp4"
            ),
            type="video",
            width=1280,
            height=720,
        )
        home = HomePage.objects.first()
        page = FlexiblePage(
            title="Vidéo dim",
            slug="video-dim",
            body=[("hosted_video", {"video": media})],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        body = client.get("/video-dim/").content.decode()
        assert 'width="1280"' in body
        assert 'height="720"' in body


class TestAmbientVideoBlock:
    """Bloc « Vidéo d'ambiance » : lecture auto, muette, en boucle, sans
    contrôles (autoplay impose muted côté navigateur)."""

    @pytest.fixture
    def page_with_ambient(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from wagtailmedia.models import get_media_model

        media = get_media_model().objects.create(
            title="Boucle d'ambiance",
            file=SimpleUploadedFile(
                "ambiance.mp4", b"\x00\x00\x00\x18ftypmp42", content_type="video/mp4"
            ),
            type="video",
        )
        home = HomePage.objects.first()
        page = FlexiblePage(
            title="Ambiance",
            slug="ambiance",
            body=[("ambient_video", {"video": media})],
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        return page

    def test_autoplays_muted_looped_without_controls(self, client, page_with_ambient):
        body = client.get("/ambiance/").content.decode()

        assert "custom-section__video-player--ambient" in body
        # Autoplay autorisé uniquement si muet + inline ; boucle activée par défaut.
        assert "autoplay" in body
        assert "muted" in body
        assert "playsinline" in body
        assert "loop" in body
        # Pas de contrôles natifs sur une vidéo d'ambiance.
        assert "controls" not in body
