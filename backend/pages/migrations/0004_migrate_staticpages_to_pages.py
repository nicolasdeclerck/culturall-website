"""Migre les `StaticPage` (snippets) vers des `StaticContentPage` (Page Wagtail).

Pour chaque snippet existant, on crée une `StaticContentPage` enfant direct
de la `HomePage`, avec le même slug, titre et contenu. Les slugs des deux
pages seedées (`a-propos`, `mentions-legales`) sont conservés tels quels :
le frontend Next.js les référence en dur.

La migration est idempotente : si une `StaticContentPage` portant le même
slug existe déjà sous la `HomePage`, le snippet correspondant est ignoré.
"""

from django.db import migrations


def migrate_static_pages_to_pages(apps, schema_editor):
    StaticPage = apps.get_model("pages", "StaticPage")

    # La manipulation d'arbre Wagtail (add_child, MP_Node) requiert les
    # modèles runtime, pas ceux retournés par apps.get_model.
    from pages.models import StaticContentPage as RuntimeStaticContentPage
    from wagtail.models import Page

    # On récupère la HomePage comme `Page` de base (et non via le modèle
    # runtime HomePage) : treebeard re-SELECT le parent via sa propre classe,
    # et le modèle runtime HomePage chargerait des colonnes (ex. hero_title)
    # absentes tant que home.0004 n'a pas tourné sur une base fraîche.
    home = Page.objects.filter(
        content_type__app_label="home", content_type__model="homepage"
    ).first()
    if home is None:
        return

    existing_slugs = set(
        RuntimeStaticContentPage.objects.descendant_of(home)
        .values_list("slug", flat=True)
    )

    for snippet in StaticPage.objects.all().order_by("slug"):
        if snippet.slug in existing_slugs:
            continue

        # locale_id explicite : sans lui, Page.save() appelle get_default_locale()
        # qui résout le parent via parent.specific_class (HomePage) et SELECT
        # ses colonnes propres (hero_*), absentes tant que home.0004 n'a pas
        # tourné sur une base fraîche.
        page = RuntimeStaticContentPage(
            title=snippet.title,
            slug=snippet.slug,
            body=snippet.body,
            live=snippet.live,
            has_unpublished_changes=snippet.has_unpublished_changes,
            first_published_at=snippet.first_published_at,
            last_published_at=snippet.last_published_at,
            locale_id=home.locale_id,
        )
        home.add_child(instance=page)
        existing_slugs.add(snippet.slug)

        # Crée une révision initiale pour que l'historique de publication
        # soit lisible dans l'admin Wagtail.
        if snippet.live:
            page.save_revision().publish()
        else:
            page.save_revision()


def reverse_migrate(apps, schema_editor):
    from pages.models import StaticContentPage as RuntimeStaticContentPage

    for page in list(RuntimeStaticContentPage.objects.all()):
        page.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0003_create_staticcontentpage"),
        ("home", "0003_seed_home_page"),
    ]

    operations = [
        migrations.RunPython(migrate_static_pages_to_pages, reverse_code=reverse_migrate),
    ]
