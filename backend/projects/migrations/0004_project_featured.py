from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_rich_text_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="featured",
            field=models.BooleanField(default=False, verbose_name="À la une"),
        ),
    ]
