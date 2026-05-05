import json
from datetime import timedelta

import pytest
from django.test import RequestFactory
from django.utils import timezone

from blog.models import ArticlePage
from blog.views import article_detail, article_list

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


class TestArticleListEndpoint:
    def test_empty_list(self, rf):
        request = rf.get("/api/blog/articles/")
        response = article_list(request)
        assert response.status_code == 200
        assert json.loads(response.content) == []

    def test_returns_live_articles(self, rf, make_article):
        make_article(title="Live", content="<p>ok</p>")
        draft = make_article(title="Draft", content="<p>draft</p>")
        draft.unpublish()

        request = rf.get("/api/blog/articles/")
        response = article_list(request)
        data = json.loads(response.content)
        assert len(data) == 1
        assert data[0]["title"] == "Live"

    def test_response_fields(self, rf, make_article):
        article = make_article(title="Test", summary="A summary", content="<p>Content</p>")
        article.tags.add("tag1", "tag2")
        article.save()

        request = rf.get("/api/blog/articles/")
        response = article_list(request)
        data = json.loads(response.content)
        assert len(data) == 1
        item = data[0]
        assert item["id"] == article.pk
        assert item["slug"] == article.slug
        assert item["title"] == "Test"
        assert item["summary"] == "A summary"
        assert "<p>" in item["content"]
        assert item["illustration_url"] is None
        assert set(item["tags"]) == {"tag1", "tag2"}
        assert "created_at" in item

    def test_ordered_newest_first(self, rf, make_article):
        old = make_article(title="Old", content="<p>old</p>")
        ArticlePage.objects.filter(pk=old.pk).update(
            first_published_at=timezone.now() - timedelta(days=1)
        )
        make_article(title="New", content="<p>new</p>")

        request = rf.get("/api/blog/articles/")
        data = json.loads(article_list(request).content)
        assert data[0]["title"] == "New"
        assert data[1]["title"] == "Old"

    def test_limit_parameter(self, rf, make_article):
        for i in range(5):
            make_article(title=f"Article {i}", content=f"<p>{i}</p>")

        request = rf.get("/api/blog/articles/", {"limit": "2"})
        data = json.loads(article_list(request).content)
        assert len(data) == 2

    def test_limit_negative_ignored(self, rf, make_article):
        make_article(title="A", content="<p>a</p>")

        request = rf.get("/api/blog/articles/", {"limit": "-1"})
        data = json.loads(article_list(request).content)
        assert len(data) == 1

    def test_limit_invalid_ignored(self, rf, make_article):
        make_article(title="A", content="<p>a</p>")

        request = rf.get("/api/blog/articles/", {"limit": "abc"})
        data = json.loads(article_list(request).content)
        assert len(data) == 1

    def test_tag_filter(self, rf, make_article):
        a1 = make_article(title="Django", content="<p>d</p>")
        a1.tags.add("python")
        a1.save()
        a2 = make_article(title="React", content="<p>r</p>")
        a2.tags.add("javascript")
        a2.save()

        request = rf.get("/api/blog/articles/", {"tag": "python"})
        data = json.loads(article_list(request).content)
        assert len(data) == 1
        assert data[0]["title"] == "Django"

    def test_tag_filter_no_match(self, rf, make_article):
        make_article(title="A", content="<p>a</p>")

        request = rf.get("/api/blog/articles/", {"tag": "nonexistent"})
        data = json.loads(article_list(request).content)
        assert len(data) == 0

    def test_only_get_allowed(self, rf):
        request = rf.post("/api/blog/articles/")
        response = article_list(request)
        assert response.status_code == 405


class TestArticleDetailEndpoint:
    def test_returns_article_by_slug(self, rf, make_article):
        article = make_article(
            title="Mon article",
            slug="mon-article",
            summary="Résumé",
            content="<p>Contenu</p>",
        )
        article.tags.add("python")
        article.save()

        request = rf.get("/api/blog/articles/mon-article/")
        response = article_detail(request, slug="mon-article")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "mon-article"
        assert data["title"] == "Mon article"
        assert data["summary"] == "Résumé"
        assert "<p>" in data["content"]
        assert data["tags"] == ["python"]

    def test_returns_404_for_unknown_slug(self, rf):
        from django.http import Http404

        request = rf.get("/api/blog/articles/unknown/")
        with pytest.raises(Http404):
            article_detail(request, slug="unknown")

    def test_does_not_return_drafts(self, rf, make_article):
        article = make_article(title="Brouillon", slug="brouillon", content="<p>x</p>")
        article.unpublish()

        from django.http import Http404

        request = rf.get("/api/blog/articles/brouillon/")
        with pytest.raises(Http404):
            article_detail(request, slug="brouillon")
