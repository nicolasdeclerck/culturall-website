import pytest
from django.core.exceptions import ValidationError
from django.test import Client

from projects.models import MAX_FEATURED_PROJECTS, Project

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


class TestProjectFeaturedView:
    url = "/api/projects/featured/"

    def test_empty_when_no_featured(self, client: Client):
        Project.objects.create(
            title="Not featured",
            youtube_url="https://youtube.com/watch?v=aaa",
            featured=False,
        )
        resp = client.get(self.url)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_only_featured(self, client: Client):
        Project.objects.create(
            title="Featured",
            youtube_url="https://youtube.com/watch?v=aaa",
            featured=True,
        )
        Project.objects.create(
            title="Not featured",
            youtube_url="https://youtube.com/watch?v=bbb",
            featured=False,
        )
        resp = client.get(self.url)
        data = resp.json()
        assert len(data) == 1
        assert data[0]["title"] == "Featured"

    def test_post_not_allowed(self, client: Client):
        resp = client.post(self.url)
        assert resp.status_code == 405


class TestProjectModel:
    def test_str(self, db):
        project = Project(title="Mon spectacle")
        assert str(project) == "Mon spectacle"

    def test_featured_default_false(self, db):
        project = Project.objects.create(
            title="Test", youtube_url="https://youtube.com/watch?v=x"
        )
        assert project.featured is False

    def test_featured_max_validation(self, db):
        for i in range(MAX_FEATURED_PROJECTS):
            Project.objects.create(
                title=f"Featured {i}",
                youtube_url=f"https://youtube.com/watch?v={i}",
                featured=True,
            )
        extra = Project(
            title="One too many",
            youtube_url="https://youtube.com/watch?v=extra",
            featured=True,
        )
        with pytest.raises(ValidationError) as exc_info:
            extra.clean()
        assert "featured" in exc_info.value.message_dict

    def test_featured_max_validation_on_save(self, db):
        """save() must also enforce the max featured constraint."""
        for i in range(MAX_FEATURED_PROJECTS):
            Project.objects.create(
                title=f"Featured {i}",
                youtube_url=f"https://youtube.com/watch?v={i}",
                featured=True,
            )
        extra = Project(
            title="One too many",
            youtube_url="https://youtube.com/watch?v=extra",
            featured=True,
        )
        with pytest.raises(ValidationError) as exc_info:
            extra.save()
        assert "featured" in exc_info.value.message_dict
        assert Project.objects.filter(featured=True).count() == MAX_FEATURED_PROJECTS

    def test_featured_allows_update_existing(self, db):
        project = Project.objects.create(
            title="Already featured",
            youtube_url="https://youtube.com/watch?v=x",
            featured=True,
        )
        for i in range(MAX_FEATURED_PROJECTS - 1):
            Project.objects.create(
                title=f"Featured {i}",
                youtube_url=f"https://youtube.com/watch?v={i}",
                featured=True,
            )
        # Re-saving an existing featured project should not raise
        project.save()
