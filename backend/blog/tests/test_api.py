import json

import pytest
from django.test import RequestFactory

from blog.models import Article
from blog.views import article_list

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

    def test_returns_live_articles(self, rf):
        a1 = Article.objects.create(title="Live", content="<p>ok</p>")
        a2 = Article.objects.create(title="Draft", content="<p>draft</p>")
        a2.unpublish()
        a2.save()

        request = rf.get("/api/blog/articles/")
        response = article_list(request)
        data = json.loads(response.content)
        assert len(data) == 1
        assert data[0]["title"] == "Live"

    def test_response_fields(self, rf):
        article = Article.objects.create(
            title="Test",
            summary="A summary",
            content="<p>Content</p>",
        )
        article.tags.add("tag1", "tag2")
        article.save()

        request = rf.get("/api/blog/articles/")
        response = article_list(request)
        data = json.loads(response.content)
        assert len(data) == 1
        item = data[0]
        assert item["id"] == article.pk
        assert item["title"] == "Test"
        assert item["summary"] == "A summary"
        assert "<p>" in item["content"]
        assert item["illustration_url"] is None
        assert set(item["tags"]) == {"tag1", "tag2"}
        assert "created_at" in item

    def test_ordered_newest_first(self, rf):
        Article.objects.create(title="Old", content="<p>old</p>")
        Article.objects.create(title="New", content="<p>new</p>")

        request = rf.get("/api/blog/articles/")
        data = json.loads(article_list(request).content)
        assert data[0]["title"] == "New"
        assert data[1]["title"] == "Old"

    def test_limit_parameter(self, rf):
        for i in range(5):
            Article.objects.create(title=f"Article {i}", content=f"<p>{i}</p>")

        request = rf.get("/api/blog/articles/", {"limit": "2"})
        data = json.loads(article_list(request).content)
        assert len(data) == 2

    def test_limit_invalid_ignored(self, rf):
        Article.objects.create(title="A", content="<p>a</p>")

        request = rf.get("/api/blog/articles/", {"limit": "abc"})
        data = json.loads(article_list(request).content)
        assert len(data) == 1

    def test_tag_filter(self, rf):
        a1 = Article.objects.create(title="Django", content="<p>d</p>")
        a1.tags.add("python")
        a1.save()
        a2 = Article.objects.create(title="React", content="<p>r</p>")
        a2.tags.add("javascript")
        a2.save()

        request = rf.get("/api/blog/articles/", {"tag": "python"})
        data = json.loads(article_list(request).content)
        assert len(data) == 1
        assert data[0]["title"] == "Django"

    def test_tag_filter_no_match(self, rf):
        Article.objects.create(title="A", content="<p>a</p>")

        request = rf.get("/api/blog/articles/", {"tag": "nonexistent"})
        data = json.loads(article_list(request).content)
        assert len(data) == 0

    def test_only_get_allowed(self, rf):
        request = rf.post("/api/blog/articles/")
        response = article_list(request)
        assert response.status_code == 405
