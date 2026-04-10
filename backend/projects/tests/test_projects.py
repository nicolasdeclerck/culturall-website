import pytest
from django.test import Client

from projects.models import Project

pytestmark = pytest.mark.django_db


class TestProjectListView:
    url = "/api/projects/"

    def test_empty_list(self, client: Client):
        resp = client.get(self.url)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_projects(self, client: Client):
        Project.objects.create(
            title="Spectacle A",
            youtube_url="https://youtube.com/watch?v=aaa",
        )
        Project.objects.create(
            title="Spectacle B",
            youtube_url="https://youtube.com/watch?v=bbb",
        )

        resp = client.get(self.url)
        data = resp.json()

        assert len(data) == 2
        titles = {p["title"] for p in data}
        assert titles == {"Spectacle A", "Spectacle B"}

    def test_project_fields(self, client: Client):
        Project.objects.create(
            title="Mon projet",
            description="<p>Description du projet</p>",
            youtube_url="https://youtube.com/watch?v=xyz",
        )

        resp = client.get(self.url)
        project = resp.json()[0]

        assert project["title"] == "Mon projet"
        assert "Description du projet" in project["description"]
        assert project["youtube_url"] == "https://youtube.com/watch?v=xyz"
        assert project["tags"] == []
        assert project["thumbnail_url"] is None

    def test_ordering_newest_first(self, client: Client):
        Project.objects.create(title="Old", youtube_url="https://youtube.com/watch?v=1")
        Project.objects.create(title="New", youtube_url="https://youtube.com/watch?v=2")

        resp = client.get(self.url)
        data = resp.json()
        assert data[0]["title"] == "New"
        assert data[1]["title"] == "Old"

    def test_post_not_allowed(self, client: Client):
        resp = client.post(self.url)
        assert resp.status_code == 405


class TestProjectModel:
    def test_str(self, db):
        project = Project(title="Mon spectacle")
        assert str(project) == "Mon spectacle"
