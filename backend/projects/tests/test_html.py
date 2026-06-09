"""Projets rendus côté serveur (Phase 4) : listing + filtre tag HTMX + détail."""

import pytest

pytestmark = pytest.mark.django_db

HTMX = {"HTTP_HX_REQUEST": "true"}


class TestProjectsIndex:
    def test_lists_published_projects(self, client, make_project):
        make_project(title="Projet Un")
        make_project(title="Projet Deux")

        resp = client.get("/projets/")

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Projet Un" in body
        assert "Projet Deux" in body
        assert "projets-grid" in body
        assert 'class="header"' in body

    def test_excludes_drafts(self, client, make_project):
        project = make_project(title="Brouillon")
        project.unpublish()
        assert "Brouillon" not in client.get("/projets/").content.decode()

    def test_empty_state(self, client, projects_index):
        resp = client.get("/projets/")
        assert resp.status_code == 200
        assert "Aucun projet" in resp.content.decode()

    def test_tag_filter_excludes_other_tags(self, client, make_project):
        tagged = make_project(title="Avec tag")
        tagged.tags.add("Danse")
        tagged.save()
        make_project(title="Sans tag")

        body = client.get("/projets/?tag=Danse").content.decode()
        assert "Avec tag" in body
        assert "Sans tag" not in body

    def test_htmx_returns_partial_without_layout(self, client, make_project):
        make_project(title="Projet HTMX")

        resp = client.get("/projets/", **HTMX)

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Projet HTMX" in body
        assert 'class="header"' not in body
        assert "projets-grid" in body


class TestProjectDetail:
    def test_renders_with_video(self, client, make_project):
        project = make_project(
            title="Mon Projet",
            description="<p>Une description riche</p>",
            youtube_url="https://www.youtube.com/watch?v=abcdefghijk",
        )

        resp = client.get(f"/projets/{project.slug}/")

        assert resp.status_code == 200
        body = resp.content.decode()
        assert "Mon Projet" in body
        assert "Une description riche" in body
        assert "youtube.com/embed/abcdefghijk" in body
        assert "project-detail" in body
        assert 'href="/projets/"' in body

    def test_404_for_unknown_slug(self, client, projects_index):
        assert client.get("/projets/inexistant/").status_code == 404

    def test_404_for_unpublished(self, client, make_project):
        project = make_project(title="Caché")
        project.unpublish()
        assert client.get(f"/projets/{project.slug}/").status_code == 404

    def test_only_get_allowed(self, client, make_project):
        project = make_project(title="X")
        assert client.post(f"/projets/{project.slug}/").status_code == 405

    def test_native_preview_renders_template(self, make_project):
        """La preview Wagtail native rend le template projet (plus de headless)."""
        project = make_project(title="Projet aperçu", description="<p>desc brouillon</p>")

        response = project.make_preview_request()

        assert response.status_code == 200
        body = response.content.decode()
        assert "Projet aperçu" in body
        assert "project-detail" in body
