import pytest
from wagtail.models import Revision

from blog.models import ArticlePage, ArticlePageTag

pytestmark = pytest.mark.django_db


class TestArticlePageModel:
    def test_str(self, make_article):
        article = make_article(title="Mon article")
        assert str(article) == "Mon article"

    def test_create_minimal(self, make_article):
        article = make_article(title="Article minimal", content="<p>Contenu obligatoire</p>")
        assert article.pk is not None
        assert article.title == "Article minimal"
        assert article.summary == ""
        assert article.illustration is None
        assert article.slug.startswith("article-")

    def test_tags(self, make_article):
        article = make_article(title="Article taggué")
        article.tags.add("django", "wagtail")
        article.save()
        assert set(article.tags.names()) == {"django", "wagtail"}

    def test_article_page_tag_model(self, make_article):
        article = make_article(title="Test tag model")
        article.tags.add("test-tag")
        article.save()
        assert ArticlePageTag.objects.filter(content_object=article).exists()

    def test_parent_is_blog_index(self, make_article, blog_index):
        article = make_article(title="Sous BlogIndex")
        assert article.get_parent().specific == blog_index


class TestArticleDraftState:
    def test_default_is_live(self, make_article):
        article = make_article(title="Article live")
        assert article.live is True

    def test_unpublish(self, make_article):
        article = make_article(title="Article à dépublier")
        article.unpublish()
        article.refresh_from_db()
        assert article.live is False


class TestArticleRevisions:
    def test_save_revision(self, make_article):
        article = make_article(title="V1", content="<p>version 1</p>")
        article.save_revision()
        # Wagtail crée déjà une revision lors du add_child publication initial
        assert (
            Revision.objects.filter(
                content_type__app_label="blog",
                content_type__model="articlepage",
                object_id=str(article.pk),
            ).count()
            >= 1
        )

    def test_multiple_revisions(self, make_article):
        article = make_article(title="V1", content="<p>version 1</p>")
        first_count = Revision.objects.filter(
            content_type__app_label="blog",
            content_type__model="articlepage",
            object_id=str(article.pk),
        ).count()
        article.title = "V2"
        article.save()
        article.save_revision()
        new_count = Revision.objects.filter(
            content_type__app_label="blog",
            content_type__model="articlepage",
            object_id=str(article.pk),
        ).count()
        assert new_count > first_count
