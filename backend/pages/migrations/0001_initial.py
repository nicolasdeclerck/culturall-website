import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaticPage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "live",
                    models.BooleanField(default=True, editable=False, verbose_name="live"),
                ),
                (
                    "has_unpublished_changes",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        verbose_name="has unpublished changes",
                    ),
                ),
                (
                    "first_published_at",
                    models.DateTimeField(
                        blank=True,
                        db_index=True,
                        null=True,
                        verbose_name="first published at",
                    ),
                ),
                (
                    "last_published_at",
                    models.DateTimeField(
                        editable=False,
                        null=True,
                        verbose_name="last published at",
                    ),
                ),
                (
                    "go_live_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="go live date/time",
                    ),
                ),
                (
                    "expire_at",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="expiry date/time",
                    ),
                ),
                (
                    "expired",
                    models.BooleanField(default=False, editable=False, verbose_name="expired"),
                ),
                (
                    "slug",
                    models.SlugField(
                        choices=[
                            ("mentions-legales", "Mentions légales"),
                            ("a-propos", "À propos"),
                        ],
                        help_text="Identifie la page côté frontend (ne pas modifier).",
                        max_length=64,
                        unique=True,
                        verbose_name="Identifiant",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Titre")),
                ("body", wagtail.fields.RichTextField(blank=True, verbose_name="Contenu")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "latest_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="latest revision",
                    ),
                ),
                (
                    "live_revision",
                    models.ForeignKey(
                        blank=True,
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailcore.revision",
                        verbose_name="live revision",
                    ),
                ),
            ],
            options={
                "verbose_name": "Page statique",
                "verbose_name_plural": "Pages statiques",
                "ordering": ["slug"],
            },
        ),
    ]
