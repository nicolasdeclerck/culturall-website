from django.db import migrations

SEED_PAGES = [
    {
        "slug": "mentions-legales",
        "title": "Mentions légales",
        "body": (
            "<p><em>Contenu à compléter depuis l'admin Wagtail.</em></p>"
            "<p>Cette page doit contenir les mentions légales obligatoires : "
            "éditeur du site, hébergeur, directeur de publication, "
            "informations RGPD, etc.</p>"
        ),
    },
    {
        "slug": "a-propos",
        "title": "À propos",
        "body": (
            "<p>Cultur'all est un projet dédié à la promotion de la culture "
            "sous toutes ses formes.</p>"
            "<p><em>Contenu à compléter depuis l'admin Wagtail.</em></p>"
        ),
    },
]


def seed_pages(apps, schema_editor):
    StaticPage = apps.get_model("pages", "StaticPage")
    for page_data in SEED_PAGES:
        StaticPage.objects.get_or_create(
            slug=page_data["slug"],
            defaults={
                "title": page_data["title"],
                "body": page_data["body"],
            },
        )


def unseed_pages(apps, schema_editor):
    StaticPage = apps.get_model("pages", "StaticPage")
    StaticPage.objects.filter(
        slug__in=[p["slug"] for p in SEED_PAGES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_pages, reverse_code=unseed_pages),
    ]
