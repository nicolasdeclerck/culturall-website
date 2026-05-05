"""Supprime l'ancien Snippet Article et son through-model ArticleTag.

À jouer après la data migration 0003 qui a recopié les Articles dans des
ArticlePages. Plus aucun code de l'application ne référence Article après
cette migration.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_migrate_articles_to_pages"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="tags",
        ),
        migrations.DeleteModel(
            name="ArticleTag",
        ),
        migrations.DeleteModel(
            name="Article",
        ),
    ]
