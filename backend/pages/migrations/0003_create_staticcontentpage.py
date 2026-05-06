"""Crée le modèle Wagtail Page `StaticContentPage`.

Le modèle cohabite temporairement avec l'ancien snippet `StaticPage` ; la
data migration 0004 recopiera le contenu, puis 0005 supprimera le snippet.
"""

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0002_seed_static_pages"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaticContentPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("body", wagtail.fields.RichTextField(blank=True, verbose_name="Contenu")),
            ],
            options={
                "verbose_name": "Page statique",
                "verbose_name_plural": "Pages statiques",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.AlterModelOptions(
            name="staticpage",
            options={
                "ordering": ["slug"],
                "verbose_name": "Page statique (legacy)",
                "verbose_name_plural": "Pages statiques (legacy)",
            },
        ),
    ]
