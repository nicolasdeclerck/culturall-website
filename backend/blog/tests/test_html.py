"""Blog rendu côté serveur (Phase 3) : listing + filtre par tag HTMX + article."""

import pytest

pytestmark = pytest.mark.django_db

HTMX = {"HTTP_HX_REQUEST": "true"}


class TestBlogIndex:
    def test_lists_published_articles(self, client, make_article):
        make_article(title="Premier article")
        make_article(title="Second article")

        resp = client.get("/blog/")

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Premier article" in body
        assert "Second article" in body
        assert "blog-masonry" in body
        # Page complète → layout de base présent
        assert 'class="header"' in body

    def test_excludes_drafts(self, client, make_article):
        article = make_article(title="Brouillon")
        article.unpublish()

        resp = client.get("/blog/")
        assert "Brouillon" not in resp.content.decode()

    def test_empty_state(self, client, blog_index):
        resp = client.get("/blog/")
        assert resp.status_code == 200
        assert "Aucun article" in resp.content.decode()

    def test_tag_filter_excludes_other_tags(self, client, make_article):
        tagged = make_article(title="Avec tag")
        tagged.tags.add("Actualité")
        tagged.save()  # modelcluster : les tags ne sont persistés qu'au save()
        make_article(title="Sans tag")

        body = client.get("/blog/?tag=Actualité").content.decode()
        assert "Avec tag" in body
        assert "Sans tag" not in body

    def test_filter_chips_list_all_tags(self, client, make_article):
        article = make_article(title="A")
        article.tags.add("Actualité", "Culture")
        article.save()

        body = client.get("/blog/").content.decode()
        assert "blog-filters" in body
        assert "Actualité" in body
        assert "Culture" in body

    def test_htmx_returns_partial_without_layout(self, client, make_article):
        make_article(title="Article HTMX")

        resp = client.get("/blog/", **HTMX)

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Article HTMX" in body
        # Partial seul : pas de <header> du layout de base
        assert 'class="header"' not in body
        assert "blog-masonry" in body


class TestArticleDetail:
    def test_renders_published_article(self, client, make_article):
        article = make_article(title="Mon Article", content="<p>Contenu riche ici</p>")
        article.tags.add("Actualité")
        article.save()

        resp = client.get(f"/blog/{article.slug}/")

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Mon Article" in body
        assert "Contenu riche ici" in body
        assert "Actualité" in body
        assert "article-detail" in body
        assert 'href="/blog/"' in body  # lien retour

    def test_404_for_unknown_slug(self, client, blog_index):
        assert client.get("/blog/inexistant/").status_code == 404

    def test_404_for_unpublished(self, client, make_article):
        article = make_article(title="Caché")
        article.unpublish()
        assert client.get(f"/blog/{article.slug}/").status_code == 404

    def test_only_get_allowed(self, client, make_article):
        article = make_article(title="X")
        assert client.post(f"/blog/{article.slug}/").status_code == 405

    def test_native_preview_renders_template(self, make_article):
        """La preview Wagtail native rend le template article (plus de headless)."""
        article = make_article(title="Brouillon aperçu", content="<p>contenu brouillon</p>")

        response = article.make_preview_request()

        assert response.status_code == 200
        body = response.content.decode()
        assert "Brouillon aperçu" in body
        assert "article-detail" in body
