import pytest

from pages.models import StaticContentPage

pytestmark = pytest.mark.django_db


class TestSeedDataMigration:
    """Verify the data migration created the two expected pages."""

    def test_seeded_pages_exist(self):
        assert StaticContentPage.objects.filter(slug="mentions-legales").exists()
        assert StaticContentPage.objects.filter(slug="a-propos").exists()

    def test_seeded_pages_are_live(self):
        for slug in ("mentions-legales", "a-propos"):
            page = StaticContentPage.objects.get(slug=slug)
            assert page.live is True

    def test_seeded_pages_are_children_of_home(self):
        from home.models import HomePage

        home = HomePage.objects.first()
        assert home is not None
        for slug in ("mentions-legales", "a-propos"):
            page = StaticContentPage.objects.get(slug=slug)
            assert page.get_parent().specific == home
