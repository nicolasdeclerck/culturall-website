import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0002_project_thumbnail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="description",
            field=wagtail.fields.RichTextField(
                blank=True, verbose_name="Description"
            ),
        ),
    ]
