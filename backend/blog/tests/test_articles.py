import pytest
from wagtail.models import Revision

from blog.models import Article, ArticleTag

pytestmark = pytest.mark.django_db


class TestArticleModel:
    def test_str(self):
        article = Article(title="Mon article")
        assert str(article) == "Mon article"

    def test_create_minimal(self):
        article = Article.objects.create(
            title="Article minimal",
            content="<p>Contenu obligatoire</p>",
        )
        assert article.pk is not None
        assert article.title == "Article minimal"
        assert article.summary == ""
        assert article.illustration is None

    def test_ordering_newest_first(self):
        a1 = Article.objects.create(title="Old", content="<p>old</p>")
        a2 = Article.objects.create(title="New", content="<p>new</p>")
        articles = list(Article.objects.all())
        assert articles[0].pk == a2.pk
        assert articles[1].pk == a1.pk

    def test_tags(self):
        article = Article.objects.create(
            title="Article taggué",
            content="<p>contenu</p>",
        )
        article.tags.add("django", "wagtail")
        article.save()
        assert set(article.tags.names()) == {"django", "wagtail"}

    def test_article_tag_model(self):
        article = Article.objects.create(
            title="Test tag model",
            content="<p>contenu</p>",
        )
        article.tags.add("test-tag")
        article.save()
        assert ArticleTag.objects.filter(content_object=article).exists()


class TestArticleDraftState:
    def test_default_is_live(self):
        article = Article.objects.create(
            title="Article live",
            content="<p>contenu</p>",
        )
        assert article.live is True

    def test_unpublish(self):
        article = Article.objects.create(
            title="Article à dépublier",
            content="<p>contenu</p>",
        )
        article.unpublish()
        article.refresh_from_db()
        assert article.live is False


class TestArticleRevisions:
    def test_save_revision(self):
        article = Article.objects.create(
            title="V1",
            content="<p>version 1</p>",
        )
        article.save_revision()
        assert Revision.objects.filter(
            content_type__app_label="blog",
            content_type__model="article",
            object_id=str(article.pk),
        ).count() == 1

    def test_multiple_revisions(self):
        article = Article.objects.create(
            title="V1",
            content="<p>version 1</p>",
        )
        article.save_revision()
        article.title = "V2"
        article.save()
        article.save_revision()
        assert Revision.objects.filter(
            content_type__app_label="blog",
            content_type__model="article",
            object_id=str(article.pk),
        ).count() == 2
