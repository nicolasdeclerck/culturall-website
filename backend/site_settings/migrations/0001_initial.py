from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
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
                    "require_authentication",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Si activé, le site n'est accessible qu'aux utilisateurs "
                            "connectés. Les comptes sont gérés via l'admin Wagtail."
                        ),
                        verbose_name="Authentification requise",
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.site",
                    ),
                ),
            ],
            options={
                "verbose_name": "Paramètres du site",
                "verbose_name_plural": "Paramètres du site",
            },
        ),
    ]
