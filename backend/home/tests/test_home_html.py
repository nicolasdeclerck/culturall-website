"""Page d'accueil rendue côté serveur (Phase 4) : landing + projets à la une + réseau."""

import pytest

from home.models import HomePage
from network.models import NetworkMember

pytestmark = pytest.mark.django_db


class TestHomePage:
    def test_renders_landing_and_sections(self, client, make_project, feature_projects):
        feature_projects(make_project(title="Projet à la une"))
        NetworkMember.objects.create(name="Partenaire A", member_type="Partenaire")

        resp = client.get("/")

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "landing-video" in body
        assert "projects-section" in body
        assert "Projet à la une" in body
        assert "network-section" in body
        assert "Partenaire A" in body

    def test_only_selected_projects_shown(self, client, make_project, feature_projects):
        feature_projects(make_project(title="En avant"))
        make_project(title="Pas en avant")

        body = client.get("/").content.decode()
        assert "En avant" in body
        assert "Pas en avant" not in body

    def test_selected_projects_keep_admin_order(self, client, make_project, feature_projects):
        alpha = make_project(title="Projet Alpha")
        beta = make_project(title="Projet Beta")
        # Ordre choisi dans l'admin : Beta puis Alpha (indépendant des dates).
        feature_projects(beta, alpha)

        body = client.get("/").content.decode()
        assert body.index("Projet Beta") < body.index("Projet Alpha")

    def test_featured_section_title_is_editable(self, client, make_project, feature_projects):
        feature_projects(make_project(title="Un projet"))
        home = HomePage.objects.first()
        home.featured_projects_title = "Nos coups de cœur"
        home.save()

        body = client.get("/").content.decode()
        assert "Nos coups de cœur" in body
        assert "Les projets à la une" not in body

    def test_no_projects_section_when_none_selected(self, client, make_project):
        make_project(title="Projet non sélectionné")

        body = client.get("/").content.decode()
        assert "projects-section" not in body

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
