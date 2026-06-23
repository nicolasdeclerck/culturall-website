"""Page d'accueil rendue côté serveur (Phase 4) : landing + réseau."""

import pytest

from network.models import NetworkMember

pytestmark = pytest.mark.django_db


class TestHomePage:
    def test_renders_landing_and_sections(self, client, make_project):
        make_project(title="Un projet")  # garantit l'existence de la HomePage
        NetworkMember.objects.create(name="Partenaire A", member_type="Partenaire")

        resp = client.get("/")

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "landing-video" in body
        assert "network-section" in body
        assert "Partenaire A" in body

    def test_network_type_filter_chips(self, client, make_project):
        make_project(title="P")  # garantit l'existence de la HomePage
        NetworkMember.objects.create(name="A", member_type="Partenaire")
        NetworkMember.objects.create(name="B", member_type="Financeur")

        body = client.get("/").content.decode()
        assert "network-filters" in body
        assert "Partenaire" in body
        assert "Financeur" in body

    def test_no_network_section_when_empty(self, client, make_project):
        make_project(title="P")
        body = client.get("/").content.decode()
        assert "network-section" not in body

    def test_head_request_allowed(self, client, make_project):
        make_project(title="P")
        assert client.head("/").status_code == 200
