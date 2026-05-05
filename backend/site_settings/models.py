import logging
import os
import subprocess
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images import get_image_model_string

logger = logging.getLogger(__name__)

FFMPEG_TIMEOUT_SECONDS = 600


@register_setting
class SiteSettings(BaseSiteSetting):
    logo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Logo du site",
        help_text=(
            "Logo affiché dans l'en-tête à la place du titre textuel. "
            "Formats recommandés : PNG ou SVG, max 500 Ko."
        ),
    )

    require_authentication = models.BooleanField(
        default=True,
        verbose_name="Authentification requise",
        help_text=(
            "Si activé, le site n'est accessible qu'aux utilisateurs connectés. "
            "Les comptes sont gérés via l'admin Wagtail."
        ),
    )

    background_video = models.FileField(
        upload_to="hero/",
        null=True,
        blank=True,
        verbose_name="Vidéo de fond (page d'accueil)",
        help_text=(
            "Vidéo lue en boucle, muette, en fond de la page d'accueil. "
            "Format source recommandé : MP4 H.264, durée 10-30s, max 50 Mo. "
            "La vidéo est automatiquement transcompressée à l'upload "
            "(H.264, max 1080p, sans audio) — la sauvegarde peut prendre "
            "plusieurs secondes."
        ),
    )

    background_video_poster = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image de poster vidéo",
        help_text=(
            "Image affichée pendant le chargement de la vidéo de fond. "
            "Optionnel : si vide, la première image de la vidéo est utilisée."
        ),
    )

    panels = [
        FieldPanel("logo"),
        FieldPanel("background_video"),
        FieldPanel("background_video_poster"),
        FieldPanel("require_authentication"),
    ]

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_video_name = (
            self.background_video.name if self.background_video else None
        )

    def save(self, *args, **kwargs):
        current_name = self.background_video.name if self.background_video else None
        if current_name and current_name != self._initial_video_name:
            self._transcode_background_video()
        super().save(*args, **kwargs)
        self._initial_video_name = (
            self.background_video.name if self.background_video else None
        )

    def _transcode_background_video(self):
        """Replace `background_video` with an H.264 / 1080p / no-audio version.

        Runs ffmpeg synchronously on the freshly uploaded file before it is
        committed to storage, then swaps the field's content with the
        transcoded output. Raises ValidationError on failure so the admin
        sees an explicit error message.
        """
        with tempfile.NamedTemporaryFile(suffix=".src", delete=False) as src_file:
            for chunk in self.background_video.chunks():
                src_file.write(chunk)
            src_path = src_file.name
        dst_path = src_path + ".out.mp4"

        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i", src_path,
                    "-vf",
                    "scale='min(1920,iw)':'min(1080,ih)':"
                    "force_original_aspect_ratio=decrease",
                    "-c:v", "libx264",
                    "-preset", "medium",
                    "-crf", "23",
                    "-pix_fmt", "yuv420p",
                    "-an",
                    "-movflags", "+faststart",
                    dst_path,
                ],
                check=True,
                capture_output=True,
                timeout=FFMPEG_TIMEOUT_SECONDS,
            )
        except FileNotFoundError as exc:
            self._cleanup_paths(src_path, dst_path)
            raise ValidationError(
                "ffmpeg n'est pas installé sur le serveur — "
                "impossible de transcompresser la vidéo."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            self._cleanup_paths(src_path, dst_path)
            raise ValidationError(
                f"La transcompression a dépassé {FFMPEG_TIMEOUT_SECONDS}s. "
                "Essaie avec une vidéo source plus courte ou plus légère."
            ) from exc
        except subprocess.CalledProcessError as exc:
            self._cleanup_paths(src_path, dst_path)
            stderr_tail = (exc.stderr or b"").decode("utf-8", errors="replace")[-500:]
            logger.error("ffmpeg transcode failed: %s", stderr_tail)
            raise ValidationError(
                "Échec de la transcompression de la vidéo "
                "(format source non lisible par ffmpeg)."
            ) from exc

        original_basename = os.path.basename(self.background_video.name)
        base, _ = os.path.splitext(original_basename)
        new_name = f"{base}.h264.mp4"
        with open(dst_path, "rb") as transcoded:
            self.background_video.save(
                new_name, ContentFile(transcoded.read()), save=False
            )

        self._cleanup_paths(src_path, dst_path)

    @staticmethod
    def _cleanup_paths(*paths):
        for path in paths:
            try:
                os.unlink(path)
            except OSError:
                pass
