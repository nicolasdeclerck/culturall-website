"""Supprime l'ancien Snippet Project et son through-model ProjectTag.

À jouer après la data migration 0007 qui a recopié les Projects dans des
ProjectPages. Plus aucun code de l'application ne référence Project après
cette migration.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0007_migrate_projects_to_pages"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="tags",
        ),
        migrations.DeleteModel(
            name="ProjectTag",
        ),
        migrations.DeleteModel(
            name="Project",
        ),
    ]
