import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailimages", "0026_delete_uploadedimage"),
        ("site_settings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="logo",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Logo affiché dans l'en-tête à la place du titre textuel. "
                    "Formats recommandés : PNG ou SVG, max 500 Ko."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
                verbose_name="Logo du site",
            ),
        ),
    ]
