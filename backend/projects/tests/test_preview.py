import json

import pytest
from django.http import Http404
from django.test import RequestFactory

from projects.views import project_preview_draft

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


class TestProjectPreviewDraftEndpoint:
    def test_returns_draft_content_with_valid_token(self, rf, make_project):
        project = make_project(title="Brouillon non publié")
        project.unpublish()

        page_preview = project.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/project/", {"token": page_preview.token})
        response = project_preview_draft(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["title"] == "Brouillon non publié"
        assert data["slug"] == project.slug

    def test_returns_draft_content_for_unpublished_project(self, rf, make_project):
        project = make_project(title="Jamais publié")
        project.unpublish()

        page_preview = project.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/project/", {"token": page_preview.token})
        response = project_preview_draft(request)
        data = json.loads(response.content)

        assert data["id"] == project.pk
        assert data["title"] == "Jamais publié"

    def test_missing_token_raises_404(self, rf):
        request = rf.get("/api/preview/project/")
        with pytest.raises(Http404):
            project_preview_draft(request)

    def test_invalid_token_raises_404(self, rf):
        request = rf.get("/api/preview/project/", {"token": "token-invalide"})
        with pytest.raises(Http404):
            project_preview_draft(request)

    def test_tampered_token_raises_404(self, rf, make_project):
        project = make_project(title="Projet test")
        page_preview = project.create_page_preview()
        page_preview.save()

        tampered = page_preview.token + "tampered"
        request = rf.get("/api/preview/project/", {"token": tampered})
        with pytest.raises(Http404):
            project_preview_draft(request)

    def test_response_fields(self, rf, make_project):
        project = make_project(
            title="Projet preview",
            slug="projet-preview",
            description="<p>Description brouillon</p>",
            year="2026",
            video_duration="3:42",
            credits="<p>Crédits brouillon</p>",
        )
        project.tags.add("preview", "test")
        project.save()

        page_preview = project.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/project/", {"token": page_preview.token})
        response = project_preview_draft(request)
        data = json.loads(response.content)

        assert data["slug"] == "projet-preview"
        assert "Description brouillon" in data["description"]
        assert data["year"] == "2026"
        assert data["video_duration"] == "3:42"
        assert "Crédits brouillon" in data["credits"]
        assert data["thumbnail_url"] is None
        assert set(data["tags"]) == {"preview", "test"}


class TestPreviewVsPublicApi:
    def test_draft_not_accessible_via_public_api(self, rf, make_project):
        """Un brouillon accessible en preview ne doit pas apparaître dans l'API publique."""
        from projects.views import project_detail

        project = make_project(title="Brouillon", slug="brouillon-test")
        project.unpublish()

        request = rf.get("/api/projects/brouillon-test/")
        with pytest.raises(Http404):
            project_detail(request, slug="brouillon-test")
