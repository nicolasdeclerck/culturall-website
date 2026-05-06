"""Migre les Projects (Snippet) vers des ProjectPages (Page Wagtail).

Étapes :
1. Crée la `ProjectsIndexPage` racine des projets (enfant de la `HomePage`).
2. Pour chaque `Project` existant, crée une `ProjectPage` enfant avec slug
   généré depuis le titre (collision-safe).
3. Recopie titre, description, youtube_url, thumbnail, year, video_duration,
   credits, featured et tags.

La migration est idempotente : si une `ProjectPage` portant le même titre
existe déjà sous la `ProjectsIndexPage`, le `Project` correspondant est ignoré.
"""

from django.db import migrations
from django.utils.text import slugify


def migrate_projects_to_pages(apps, schema_editor):
    # Idempotence : si la table source a déjà été droppée par la migration
    # successeur (0008), on no-op pour éviter un crash quand la chaîne est
    # rejouée sur une DB déjà avancée (ex : `migrate --fake` puis `migrate`
    # depuis zéro après un reset, ou cascade après InconsistentMigrationHistory).
    from django.db import connection
    if "projects_project" not in connection.introspection.table_names():
        return

    Project = apps.get_model("projects", "Project")
    ProjectTag = apps.get_model("projects", "ProjectTag")

    # La manipulation d'arbre Wagtail (add_child, MP_Node) requiert les
    # modèles runtime, pas ceux retournés par apps.get_model.
    from home.models import HomePage as RuntimeHomePage
    from projects.models import ProjectPage as RuntimeProjectPage
    from projects.models import ProjectsIndexPage as RuntimeProjectsIndexPage

    home = RuntimeHomePage.objects.first()
    if home is None:
        return

    projects_index = RuntimeProjectsIndexPage.objects.descendant_of(home).first()
    if projects_index is None:
        projects_index = RuntimeProjectsIndexPage(title="Projets", slug="projets")
        home.add_child(instance=projects_index)
        projects_index.save_revision().publish()

    existing_slugs = set(projects_index.get_children().values_list("slug", flat=True))

    for project in Project.objects.all().order_by("created_at"):
        if (
            RuntimeProjectPage.objects.descendant_of(projects_index)
            .filter(title=project.title)
            .exists()
        ):
            continue

        base_slug = slugify(project.title) or "projet"
        slug = base_slug
        suffix = 2
        while slug in existing_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        existing_slugs.add(slug)

        project_page = RuntimeProjectPage(
            title=project.title,
            slug=slug,
            description=project.description,
            youtube_url=project.youtube_url,
            thumbnail_id=project.thumbnail_id,
            year=project.year,
            video_duration=project.video_duration,
            credits=project.credits,
            featured=project.featured,
            first_published_at=project.created_at,
            last_published_at=project.created_at,
        )
        projects_index.add_child(instance=project_page)

        tag_names = list(
            ProjectTag.objects.filter(content_object=project)
            .values_list("tag__name", flat=True)
        )
        if tag_names:
            project_page.tags.add(*tag_names)
            project_page.save()


def reverse_migrate(apps, schema_editor):
    from projects.models import ProjectPage as RuntimeProjectPage
    from projects.models import ProjectsIndexPage as RuntimeProjectsIndexPage

    for page in list(RuntimeProjectPage.objects.all()):
        page.delete()
    for page in list(RuntimeProjectsIndexPage.objects.all()):
        page.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0006_create_project_pages"),
        ("home", "0003_seed_home_page"),
    ]

    operations = [
        migrations.RunPython(migrate_projects_to_pages, reverse_code=reverse_migrate),
    ]
