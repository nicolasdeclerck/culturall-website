import json

import pytest
from django.http import Http404
from django.test import RequestFactory

from pages.models import StaticContentPage
from pages.views import static_page_detail, static_page_preview_draft

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


class TestStaticPageDetailEndpoint:
    def test_returns_seeded_page(self, rf):
        request = rf.get("/api/pages/mentions-legales/")
        response = static_page_detail(request, slug="mentions-legales")

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "mentions-legales"
        assert data["title"] == "Mentions légales"
        assert "<p>" in data["body"]

    def test_returns_404_when_slug_does_not_exist(self, rf):
        request = rf.get("/api/pages/inexistante/")
        with pytest.raises(Http404):
            static_page_detail(request, slug="inexistante")

    def test_returns_404_when_page_unpublished(self, rf):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.unpublish()

        request = rf.get("/api/pages/a-propos/")
        with pytest.raises(Http404):
            static_page_detail(request, slug="a-propos")

    def test_empty_body_returns_empty_string(self, rf):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.body = ""
        page.save()

        request = rf.get("/api/pages/a-propos/")
        response = static_page_detail(request, slug="a-propos")

        data = json.loads(response.content)
        assert data["body"] == ""

    def test_only_get_allowed(self, rf):
        request = rf.post("/api/pages/mentions-legales/")
        response = static_page_detail(request, slug="mentions-legales")
        assert response.status_code == 405

    def test_body_is_rendered_html(self, rf):
        page = StaticContentPage.objects.get(slug="mentions-legales")
        page.body = "<p>Hello <strong>world</strong></p>"
        page.save()

        request = rf.get("/api/pages/mentions-legales/")
        response = static_page_detail(request, slug="mentions-legales")
        data = json.loads(response.content)
        assert "<strong>" in data["body"]


class TestSeedDataMigration:
    """Verify the data migration created the two expected pages."""

    def test_seeded_pages_exist(self):
        assert StaticContentPage.objects.filter(slug="mentions-legales").exists()
        assert StaticContentPage.objects.filter(slug="a-propos").exists()

    def test_seeded_pages_are_live(self):
        for slug in ("mentions-legales", "a-propos"):
            page = StaticContentPage.objects.get(slug=slug)
            assert page.live is True

    def test_seeded_pages_are_children_of_home(self):
        from home.models import HomePage

        home = HomePage.objects.first()
        assert home is not None
        for slug in ("mentions-legales", "a-propos"):
            page = StaticContentPage.objects.get(slug=slug)
            assert page.get_parent().specific == home


class TestStaticPagePreviewDraftEndpoint:
    def test_returns_draft_content_with_valid_token(self, rf):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.body = "<p>Brouillon non publié</p>"
        page_preview = page.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/page/", {"token": page_preview.token})
        response = static_page_preview_draft(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "a-propos"
        assert "Brouillon non publié" in data["body"]

    def test_returns_draft_for_unpublished_page(self, rf):
        page = StaticContentPage.objects.get(slug="a-propos")
        page.unpublish()
        page.body = "<p>Modifs sur page dépubliée</p>"
        page_preview = page.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/page/", {"token": page_preview.token})
        response = static_page_preview_draft(request)
        data = json.loads(response.content)

        assert data["slug"] == "a-propos"
        assert "Modifs sur page dépubliée" in data["body"]

    def test_missing_token_raises_404(self, rf):
        request = rf.get("/api/preview/page/")
        with pytest.raises(Http404):
            static_page_preview_draft(request)

    def test_invalid_token_raises_404(self, rf):
        request = rf.get("/api/preview/page/", {"token": "token-invalide"})
        with pytest.raises(Http404):
            static_page_preview_draft(request)

    def test_tampered_token_raises_404(self, rf):
        page = StaticContentPage.objects.get(slug="a-propos")
        page_preview = page.create_page_preview()
        page_preview.save()

        tampered = page_preview.token + "tampered"
        request = rf.get("/api/preview/page/", {"token": tampered})
        with pytest.raises(Http404):
            static_page_preview_draft(request)
