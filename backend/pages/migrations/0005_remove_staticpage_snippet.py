"""Supprime l'ancien snippet `StaticPage`.

À jouer après la data migration 0004 qui a recopié le contenu dans des
`StaticContentPage`. Plus aucun code de l'application ne référence le
snippet après cette migration.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0004_migrate_staticpages_to_pages"),
    ]

    operations = [
        migrations.DeleteModel(
            name="StaticPage",
        ),
    ]
