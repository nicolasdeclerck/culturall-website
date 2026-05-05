"""Tests sur l'état de l'arbre Wagtail après les migrations blog/home.

On vérifie que les data migrations (`home.0003_seed_home_page`,
`blog.0003_migrate_articles_to_pages`) ont bien produit l'arbre attendu et
que la BlogIndexPage est unique et bien rattachée à la HomePage.
"""

import pytest
from wagtail.models import Site

from blog.models import BlogIndexPage
from home.models import HomePage

pytestmark = pytest.mark.django_db


class TestPostMigrationState:
    def test_home_page_created(self):
        assert HomePage.objects.count() == 1

    def test_blog_index_created_under_home(self):
        blog_index = BlogIndexPage.objects.first()
        assert blog_index is not None
        assert blog_index.slug == "blog"

        home = HomePage.objects.first()
        assert blog_index.get_parent().pk == home.pk

    def test_blog_index_is_live(self):
        blog_index = BlogIndexPage.objects.first()
        assert blog_index.live is True

    def test_default_site_points_at_home_page(self):
        site = Site.objects.filter(is_default_site=True).first()
        assert site is not None
        home = HomePage.objects.first()
        assert site.root_page_id == home.pk

    def test_blog_index_max_count_one(self):
        """La contrainte `max_count = 1` est appliquée par Wagtail."""
        assert BlogIndexPage.objects.count() == 1
        home = HomePage.objects.first()
        assert BlogIndexPage.can_create_at(home) is False
