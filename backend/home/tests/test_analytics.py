"""Injection du script Plausible (mesure d'audience) dans base.html.

Règle métier : le script n'est rendu que pour les visiteurs ANONYMES et
uniquement si la mesure est configurée (PLAUSIBLE_DOMAIN + PLAUSIBLE_SCRIPT_URL).
Les utilisateurs connectés sont exclus des statistiques.
"""

import pytest

pytestmark = pytest.mark.django_db

SCRIPT_URL = "https://stats.example.org/js/script.js"
DOMAIN = "example.org"


def _configure(settings):
    settings.PLAUSIBLE_DOMAIN = DOMAIN
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL


class TestPlausibleSnippet:
    def test_not_rendered_when_unconfigured(self, client, make_project, settings):
        # Défaut : les deux variables sont vides → pas de script.
        settings.PLAUSIBLE_DOMAIN = ""
        settings.PLAUSIBLE_SCRIPT_URL = ""
        make_project(title="P")

        body = client.get("/").content.decode()

        assert SCRIPT_URL not in body
        assert "data-domain" not in body

    def test_rendered_for_anonymous_when_configured(self, client, make_project, settings):
        _configure(settings)
        make_project(title="P")

        body = client.get("/").content.decode()

        assert SCRIPT_URL in body
        assert f'data-domain="{DOMAIN}"' in body

    def test_not_rendered_for_authenticated_user(self, client, make_project, settings, user):
        _configure(settings)
        make_project(title="P")
        client.force_login(user)

        body = client.get("/").content.decode()

        # Utilisateur connecté → exclu de la mesure, aucun script injecté.
        assert SCRIPT_URL not in body
        assert "data-domain" not in body

    def test_not_rendered_when_only_domain_set(self, client, make_project, settings):
        # Configuration partielle (URL manquante) → pas de script (garde-fou).
        settings.PLAUSIBLE_DOMAIN = DOMAIN
        settings.PLAUSIBLE_SCRIPT_URL = ""
        make_project(title="P")

        body = client.get("/").content.decode()

        assert "data-domain" not in body
