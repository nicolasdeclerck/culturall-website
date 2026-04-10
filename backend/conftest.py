import pytest
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site

from site_settings.models import SiteSettings

User = get_user_model()


@pytest.fixture()
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="Testpass123!",
    )


@pytest.fixture()
def site(db):
    """Return the default Wagtail site, creating root page if needed."""
    root = Page.objects.filter(depth=1).first()
    if root is None:
        root = Page.add_root(title="Root")
    site, _ = Site.objects.get_or_create(
        is_default_site=True,
        defaults={"root_page": root, "hostname": "localhost"},
    )
    return site


@pytest.fixture()
def site_settings(site):
    settings, _ = SiteSettings.objects.get_or_create(site=site)
    return settings


@pytest.fixture(autouse=True)
def _disable_auth_middleware(site):
    """Disable LoginRequiredMiddleware by default in all tests."""
    settings, _ = SiteSettings.objects.get_or_create(site=site)
    settings.require_authentication = False
    settings.save()
