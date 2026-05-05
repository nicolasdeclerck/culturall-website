"""Crée les Pages ProjectsIndexPage et ProjectPage et leur through-model de tags."""

import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0005_add_year_duration_credits"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
        ("wagtailcore", "0094_alter_page_locale"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectsIndexPage",
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
            ],
            options={
                "verbose_name": "Index des projets",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="ProjectPage",
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
                ("description", wagtail.fields.RichTextField(blank=True, verbose_name="Description")),
                ("youtube_url", models.URLField(verbose_name="Lien YouTube")),
                ("year", models.CharField(blank=True, max_length=20, verbose_name="Année de création")),
                ("video_duration", models.CharField(blank=True, max_length=50, verbose_name="Durée de la vidéo")),
                ("credits", wagtail.fields.RichTextField(blank=True, verbose_name="Crédits")),
                ("featured", models.BooleanField(default=False, verbose_name="À la une")),
                (
                    "thumbnail",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                        verbose_name="Miniature",
                    ),
                ),
            ],
            options={
                "verbose_name": "Projet",
                "verbose_name_plural": "Projets",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="ProjectPageTag",
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
                    "content_object",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tagged_items",
                        to="projects.projectpage",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(app_label)s_%(class)s_items",
                        to="taggit.tag",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="projectpage",
            name="tags",
            field=modelcluster.contrib.taggit.ClusterTaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="projects.ProjectPageTag",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
