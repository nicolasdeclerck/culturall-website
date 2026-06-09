import pytest
from django.utils import timezone
from wagtail.models import Page, Site

from blog.models import ArticlePage, BlogIndexPage
from home.models import HomePage


@pytest.fixture
def blog_index(db):
    """Retourne la BlogIndexPage, en reconstituant la chaîne d'arbre si besoin."""
    existing = BlogIndexPage.objects.first()
    if existing is not None:
        return existing

    home = HomePage.objects.first()
    if home is None:
        root = Page.objects.filter(depth=1).first()
        if root is None:
            root = Page.add_root(title="Root")
        home = HomePage(title="Home", slug="home")
        root.add_child(instance=home)
        site = Site.objects.filter(is_default_site=True).first()
        if site is not None:
            site.root_page = home
            site.save()

    blog_index = BlogIndexPage(title="Blog", slug="blog")
    home.add_child(instance=blog_index)
    return blog_index


@pytest.fixture
def make_article(blog_index):
    """Crée un ArticlePage publié sous la BlogIndexPage. Slug auto-incrémenté."""
    counter = {"n": 0}

    def _make(title="Article", content="<p>contenu</p>", **kwargs):
        counter["n"] += 1
        kwargs.setdefault("slug", f"article-{counter['n']}")
        # add_child() insère la page mais ne la « publie » pas : sans cela
        # first_published_at reste NULL et le tri -first_published_at devient
        # dépendant du SGBD (NULLS FIRST sur Postgres, NULLS LAST sur SQLite).
        kwargs.setdefault("first_published_at", timezone.now())
        article = ArticlePage(title=title, content=content, **kwargs)
        blog_index.add_child(instance=article)
        return article

    return _make
