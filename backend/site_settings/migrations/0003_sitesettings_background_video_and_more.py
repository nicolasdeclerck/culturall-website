import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailimages", "0026_delete_uploadedimage"),
        ("site_settings", "0002_sitesettings_logo"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="background_video",
            field=models.FileField(
                blank=True,
                help_text=(
                    "Vidéo lue en boucle, muette, en fond de la page d'accueil. "
                    "Format source recommandé : MP4 H.264, durée 10-30s, max "
                    "50 Mo. La vidéo est automatiquement transcompressée à "
                    "l'upload (H.264, max 1080p, sans audio) — la sauvegarde "
                    "peut prendre plusieurs secondes."
                ),
                null=True,
                upload_to="hero/",
                verbose_name="Vidéo de fond (page d'accueil)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="background_video_poster",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Image affichée pendant le chargement de la vidéo de fond. "
                    "Optionnel : si vide, la première image de la vidéo est "
                    "utilisée."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
                verbose_name="Image de poster vidéo",
            ),
        ),
    ]
