import pytest
from django.utils import timezone
from wagtail.models import Page, Site

from home.models import HomePage
from projects.models import ProjectPage, ProjectsIndexPage


@pytest.fixture
def home_tree(db):
    """Garantit l'arbre root → HomePage → ProjectsIndexPage et retourne l'index projets."""
    home = HomePage.objects.first()
    if home is None:
        root = Page.objects.filter(depth=1).first() or Page.add_root(title="Root")
        home = HomePage(title="Home", slug="home")
        root.add_child(instance=home)
        site = Site.objects.filter(is_default_site=True).first()
        if site is not None:
            site.root_page = home
            site.save()

    index = ProjectsIndexPage.objects.first()
    if index is None:
        index = ProjectsIndexPage(title="Projets", slug="projets")
        home.add_child(instance=index)
    return index


@pytest.fixture
def make_project(home_tree):
    """Crée un ProjectPage publié sous la ProjectsIndexPage. Slug auto-incrémenté."""
    counter = {"n": 0}

    def _make(title="Projet", youtube_url="https://youtube.com/watch?v=test", **kwargs):
        counter["n"] += 1
        kwargs.setdefault("slug", f"projet-{counter['n']}")
        kwargs.setdefault("first_published_at", timezone.now())
        project = ProjectPage(title=title, youtube_url=youtube_url, **kwargs)
        home_tree.add_child(instance=project)
        return project

    return _make
