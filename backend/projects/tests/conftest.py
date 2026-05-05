import pytest
from wagtail.models import Page, Site

from home.models import HomePage
from projects.models import ProjectPage, ProjectsIndexPage


@pytest.fixture
def projects_index(db):
    """Retourne la ProjectsIndexPage, en reconstituant la chaîne d'arbre si besoin."""
    existing = ProjectsIndexPage.objects.first()
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

    projects_index = ProjectsIndexPage(title="Projets", slug="projets")
    home.add_child(instance=projects_index)
    return projects_index


@pytest.fixture
def make_project(projects_index):
    """Crée un ProjectPage publié sous la ProjectsIndexPage. Slug auto-incrémenté."""
    counter = {"n": 0}

    def _make(title="Projet", youtube_url="https://youtube.com/watch?v=test", **kwargs):
        counter["n"] += 1
        kwargs.setdefault("slug", f"projet-{counter['n']}")
        project = ProjectPage(title=title, youtube_url=youtube_url, **kwargs)
        projects_index.add_child(instance=project)
        return project

    return _make
