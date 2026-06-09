import pytest
from django.core.exceptions import ValidationError

from projects.models import MAX_FEATURED_PROJECTS, ProjectPage, ProjectPageTag

pytestmark = pytest.mark.django_db


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
