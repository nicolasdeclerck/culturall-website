import json

import pytest
from django.http import Http404
from django.test import RequestFactory

from blog.views import article_preview_draft

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


class TestArticlePreviewDraftEndpoint:
    def test_returns_draft_content_with_valid_token(self, rf, make_article):
        article = make_article(title="Brouillon non publié", content="<p>contenu brouillon</p>")
        article.unpublish()

        page_preview = article.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/draft/", {"token": page_preview.token})
        response = article_preview_draft(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["title"] == "Brouillon non publié"
        assert "<p>" in data["content"]
        assert data["slug"] == article.slug

    def test_returns_draft_content_for_unpublished_article(self, rf, make_article):
        article = make_article(title="Jamais publié", content="<p>contenu</p>")
        article.unpublish()

        page_preview = article.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/draft/", {"token": page_preview.token})
        response = article_preview_draft(request)
        data = json.loads(response.content)

        assert data["id"] == article.pk
        assert data["title"] == "Jamais publié"

    def test_missing_token_raises_404(self, rf):
        request = rf.get("/api/preview/draft/")
        with pytest.raises(Http404):
            article_preview_draft(request)

    def test_invalid_token_raises_404(self, rf):
        request = rf.get("/api/preview/draft/", {"token": "token-invalide"})
        with pytest.raises(Http404):
            article_preview_draft(request)

    def test_tampered_token_raises_404(self, rf, make_article):
        article = make_article(title="Article test", content="<p>x</p>")
        page_preview = article.create_page_preview()
        page_preview.save()

        tampered = page_preview.token + "tampered"
        request = rf.get("/api/preview/draft/", {"token": tampered})
        with pytest.raises(Http404):
            article_preview_draft(request)

    def test_response_fields(self, rf, make_article):
        article = make_article(
            title="Article preview",
            slug="article-preview",
            summary="Résumé brouillon",
            content="<p>Contenu brouillon</p>",
        )
        article.tags.add("preview", "test")
        article.save()

        page_preview = article.create_page_preview()
        page_preview.save()

        request = rf.get("/api/preview/draft/", {"token": page_preview.token})
        response = article_preview_draft(request)
        data = json.loads(response.content)

        assert data["slug"] == "article-preview"
        assert data["summary"] == "Résumé brouillon"
        assert data["illustration_url"] is None
        assert set(data["tags"]) == {"preview", "test"}


class TestPreviewVsPublicApi:
    def test_draft_not_accessible_via_public_api(self, rf, make_article):
        """Un brouillon accessible en preview ne doit pas apparaître dans l'API publique."""
        from blog.views import article_detail

        article = make_article(title="Brouillon", slug="brouillon", content="<p>x</p>")
        article.unpublish()

        request = rf.get("/api/blog/articles/brouillon/")
        with pytest.raises(Http404):
            article_detail(request, slug="brouillon")
