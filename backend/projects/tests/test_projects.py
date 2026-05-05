import json

import pytest
from django.core.exceptions import ValidationError
from django.http import Http404
from django.test import RequestFactory

from projects.models import MAX_FEATURED_PROJECTS, ProjectPage, ProjectPageTag
from projects.views import project_detail, project_featured, project_list

pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


class TestProjectListView:
    def test_empty_list(self, rf, projects_index):
        request = rf.get("/api/projects/")
        response = project_list(request)
        assert response.status_code == 200
        assert json.loads(response.content) == []

    def test_returns_projects(self, rf, make_project):
        make_project(title="Spectacle A", youtube_url="https://youtube.com/watch?v=aaa")
        make_project(title="Spectacle B", youtube_url="https://youtube.com/watch?v=bbb")

        response = project_list(rf.get("/api/projects/"))
        data = json.loads(response.content)

        assert len(data) == 2
        titles = {p["title"] for p in data}
        assert titles == {"Spectacle A", "Spectacle B"}

    def test_project_fields(self, rf, make_project):
        project = make_project(
            title="Mon projet",
            slug="mon-projet",
            description="<p>Description du projet</p>",
            youtube_url="https://youtube.com/watch?v=xyz",
            year="2024",
            video_duration="3min30",
            credits="<p>Réalisation : Jean Dupont</p>",
        )

        response = project_list(rf.get("/api/projects/"))
        data = json.loads(response.content)
        assert len(data) == 1
        item = data[0]

        assert item["id"] == project.pk
        assert item["slug"] == "mon-projet"
        assert item["title"] == "Mon projet"
        assert "Description du projet" in item["description"]
        assert item["youtube_url"] == "https://youtube.com/watch?v=xyz"
        assert item["tags"] == []
        assert item["thumbnail_url"] is None
        assert item["year"] == "2024"
        assert item["video_duration"] == "3min30"
        assert "Réalisation : Jean Dupont" in item["credits"]

    def test_project_optional_fields_empty(self, rf, make_project):
        make_project(title="Projet sans extras", slug="projet-sans-extras")

        response = project_list(rf.get("/api/projects/"))
        item = json.loads(response.content)[0]

        assert item["year"] == ""
        assert item["video_duration"] == ""
        assert item["credits"] == ""

    def test_ordering_newest_first(self, rf, make_project):
        from datetime import timedelta

        from django.utils import timezone

        old = make_project(title="Old")
        ProjectPage.objects.filter(pk=old.pk).update(
            first_published_at=timezone.now() - timedelta(days=1)
        )
        make_project(title="New")

        response = project_list(rf.get("/api/projects/"))
        data = json.loads(response.content)
        assert data[0]["title"] == "New"
        assert data[1]["title"] == "Old"

    def test_only_get_allowed(self, rf):
        response = project_list(rf.post("/api/projects/"))
        assert response.status_code == 405

    def test_does_not_return_drafts(self, rf, make_project):
        live = make_project(title="Live")
        draft = make_project(title="Draft")
        draft.unpublish()

        response = project_list(rf.get("/api/projects/"))
        data = json.loads(response.content)
        assert len(data) == 1
        assert data[0]["title"] == "Live"


class TestProjectFeaturedView:
    def test_empty_when_no_featured(self, rf, make_project):
        make_project(title="Not featured", featured=False)

        response = project_featured(rf.get("/api/projects/featured/"))
        assert response.status_code == 200
        assert json.loads(response.content) == []

    def test_returns_only_featured(self, rf, make_project):
        make_project(title="Featured", featured=True)
        make_project(title="Not featured", featured=False)

        response = project_featured(rf.get("/api/projects/featured/"))
        data = json.loads(response.content)
        assert len(data) == 1
        assert data[0]["title"] == "Featured"

    def test_only_get_allowed(self, rf, projects_index):
        response = project_featured(rf.post("/api/projects/featured/"))
        assert response.status_code == 405


class TestProjectDetailView:
    def test_returns_project_by_slug(self, rf, make_project):
        proj = make_project(
            title="Mon projet",
            slug="mon-projet",
            youtube_url="https://youtube.com/watch?v=abc",
            year="2024",
        )
        proj.tags.add("tag1")
        proj.save()

        response = project_detail(rf.get("/api/projects/mon-projet/"), slug="mon-projet")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "mon-projet"
        assert data["title"] == "Mon projet"
        assert data["year"] == "2024"
        assert data["tags"] == ["tag1"]

    def test_returns_404_for_unknown_slug(self, rf, projects_index):
        with pytest.raises(Http404):
            project_detail(rf.get("/api/projects/unknown/"), slug="unknown")

    def test_does_not_return_drafts(self, rf, make_project):
        proj = make_project(title="Brouillon", slug="brouillon")
        proj.unpublish()

        with pytest.raises(Http404):
            project_detail(rf.get("/api/projects/brouillon/"), slug="brouillon")

    def test_only_get_allowed(self, rf, projects_index):
        response = project_detail(rf.post("/api/projects/test/"), slug="test")
        assert response.status_code == 405


class TestProjectPageModel:
    def test_str(self, make_project):
        project = make_project(title="Mon spectacle")
        assert str(project) == "Mon spectacle"

    def test_featured_default_false(self, make_project):
        project = make_project(title="Test")
        assert project.featured is False

    def test_tags(self, make_project):
        project = make_project(title="Projet taggué")
        project.tags.add("wagtail", "django")
        project.save()
        assert set(project.tags.names()) == {"wagtail", "django"}

    def test_project_page_tag_model(self, make_project):
        project = make_project(title="Test tag model")
        project.tags.add("test-tag")
        project.save()
        assert ProjectPageTag.objects.filter(content_object=project).exists()

    def test_parent_is_projects_index(self, make_project, projects_index):
        project = make_project(title="Sous ProjectsIndex")
        assert project.get_parent().specific == projects_index

    def test_featured_max_validation(self, make_project):
        for i in range(MAX_FEATURED_PROJECTS):
            make_project(title=f"Featured {i}", featured=True)
        extra = make_project(title="One too many", featured=False)
        extra.featured = True
        with pytest.raises(ValidationError) as exc_info:
            extra.clean()
        assert "featured" in exc_info.value.message_dict

    def test_featured_max_validation_on_save(self, make_project):
        """save() doit aussi appliquer la contrainte max featured."""
        for i in range(MAX_FEATURED_PROJECTS):
            make_project(title=f"Featured {i}", featured=True)
        extra = make_project(title="One too many", featured=False)
        extra.featured = True
        with pytest.raises(ValidationError) as exc_info:
            extra.save()
        assert "featured" in exc_info.value.message_dict
        assert ProjectPage.objects.filter(featured=True).count() == MAX_FEATURED_PROJECTS

    def test_featured_allows_update_existing(self, make_project):
        project = make_project(title="Already featured", featured=True)
        for i in range(MAX_FEATURED_PROJECTS - 1):
            make_project(title=f"Featured {i}", featured=True)
        # Re-saving an existing featured project should not raise
        project.save()
