import json

import pytest
from django.http import Http404
from django.test import RequestFactory

from pages.models import StaticPage
from pages.views import static_page_detail

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
        page = StaticPage.objects.get(slug="a-propos")
        page.unpublish()
        page.save()

        request = rf.get("/api/pages/a-propos/")
        with pytest.raises(Http404):
            static_page_detail(request, slug="a-propos")

    def test_empty_body_returns_empty_string(self, rf):
        page = StaticPage.objects.get(slug="a-propos")
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
        page = StaticPage.objects.get(slug="mentions-legales")
        page.body = "<p>Hello <strong>world</strong></p>"
        page.save()

        request = rf.get("/api/pages/mentions-legales/")
        response = static_page_detail(request, slug="mentions-legales")
        data = json.loads(response.content)
        assert "<strong>" in data["body"]


class TestSeedDataMigration:
    """Verify the data migration created the two expected pages."""

    def test_seeded_pages_exist(self):
        assert StaticPage.objects.filter(slug="mentions-legales").exists()
        assert StaticPage.objects.filter(slug="a-propos").exists()

    def test_seeded_pages_are_live(self):
        for slug in ("mentions-legales", "a-propos"):
            page = StaticPage.objects.get(slug=slug)
            assert page.live is True
