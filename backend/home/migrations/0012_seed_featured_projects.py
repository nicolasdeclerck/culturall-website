"""Reporte la sélection « projet à la une » existante vers le nouveau modèle.

Avant ce changement, les projets mis en avant étaient marqués via le champ
booléen `ProjectPage.featured` (limité à 3, ordonnés par date de publication).
Désormais ils sont choisis et ordonnés explicitement dans l'admin via le modèle
`FeaturedProject` rattaché à la `HomePage`. Cette data migration recopie la
sélection existante afin que la section ne se vide pas après le déploiement.

Elle s'exécute après la création de `FeaturedProject` (home 0011) et avant la
suppression du champ `featured` (projects 0009).
"""

from django.db import migrations

MAX_FEATURED_PROJECTS = 3


def copy_featured_projects(apps, schema_editor):
    HomePage = apps.get_model("home", "HomePage")
    FeaturedProject = apps.get_model("home", "FeaturedProject")
    ProjectPage = apps.get_model("projects", "ProjectPage")

    featured = list(
        ProjectPage.objects.filter(featured=True).order_by("-first_published_at")[
            :MAX_FEATURED_PROJECTS
        ]
    )
    if not featured:
        return

    for home in HomePage.objects.all():
        # Idempotence : on ne touche pas une page qui a déjà une sélection.
        if FeaturedProject.objects.filter(page_id=home.pk).exists():
            continue
        for index, project in enumerate(featured):
            FeaturedProject.objects.create(
                page_id=home.pk,
                project_id=project.pk,
                sort_order=index,
            )


def noop(apps, schema_editor):
    # La table FeaturedProject est supprimée en revenant sur 0011 ; rien à faire.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0011_homepage_featured_projects_title_featuredproject"),
        ("projects", "0008_remove_project_snippet"),
    ]

    operations = [
        migrations.RunPython(copy_featured_projects, noop),
    ]
