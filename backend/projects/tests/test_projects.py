import pytest

from projects.models import ProjectPageTag

pytestmark = pytest.mark.django_db


class TestProjectPageModel:
    def test_str(self, make_project):
        project = make_project(title="Mon spectacle")
        assert str(project) == "Mon spectacle"

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
