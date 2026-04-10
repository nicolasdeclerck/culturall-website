import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailimages", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NetworkMember",
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
                ("name", models.CharField(max_length=255, verbose_name="Nom")),
                ("member_type", models.CharField(max_length=100, verbose_name="Type")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "logo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                        verbose_name="Logo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Membre du réseau",
                "verbose_name_plural": "Membres du réseau",
                "ordering": ["name"],
            },
        ),
    ]
