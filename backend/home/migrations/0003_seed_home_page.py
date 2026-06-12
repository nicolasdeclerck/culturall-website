"""Crée la HomePage racine de l'arbre Wagtail.

Avant cette migration, le `Site` Wagtail par défaut pointait sur la page
« Welcome » créée par le bootstrap de Wagtail. Cette migration :

1. Crée une instance `HomePage` enfant de la racine Wagtail (slug=`home`).
2. Repointe le `Site` par défaut sur cette `HomePage`.
3. Supprime la welcome page si elle est encore l'unique enfant initial.

Sans cette HomePage, on ne peut pas créer de `BlogIndexPage` (qui doit être
enfant d'une HomePage) ni démarrer la migration Articles → ArticlePages.
"""

from django.db import migrations


def create_home_page(apps, schema_editor):
    # On crée la HomePage via le modèle HISTORIQUE (apps.get_model) : son état
    # à cette migration ne comporte AUCUN champ propre, donc l'INSERT ne
    # référence pas des colonnes ajoutées par des migrations ultérieures
    # (ex. hero_title/hero_subtitle en 0004) — colonnes inexistantes quand
    # cette migration s'exécute sur une base fraîche.
    #
    # Les opérations d'arbre treebeard (add_child) ne sont disponibles que sur
    # le modèle Page RUNTIME ; de plus treebeard re-SELECT le parent via la
    # classe de CE parent. On attache donc l'instance historique à la `root`
    # réelle (un `Page` de base, sans colonnes propres à HomePage) : le verrou
    # treebeard porte sur `Page` et l'INSERT sur le modèle historique — aucun
    # des deux ne touche les colonnes hero.
    HomePage = apps.get_model("home", "HomePage")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Locale = apps.get_model("wagtailcore", "Locale")

    from wagtail.models import Page, Site

    if HomePage.objects.exists():
        return

    root = Page.objects.filter(depth=1).first()
    if root is None:
        return

    # On ne supprime PAS la welcome page créée par le bootstrap Wagtail :
    # un Page.delete() déclenche un cascade qui interroge toutes les tables
    # liées à Page (wagtailforms, wagtailimages, etc.) et dépend d'un ordre
    # de migration cross-app difficile à garantir. On la renomme pour
    # libérer le slug "home". `update()` évite la logique de Page.save().
    root.get_children().filter(slug="home").update(slug="wagtail-welcome")

    home_ct, _ = ContentType.objects.get_or_create(
        app_label="home", model="homepage"
    )
    locale = Locale.objects.first()

    home_page = HomePage(
        title="Cultur'all",
        draft_title="Cultur'all",
        slug="home",
        content_type_id=home_ct.pk,
        locale_id=locale.pk,
        live=True,
        has_unpublished_changes=False,
        url_path=root.url_path + "home/",
    )
    # treebeard (sur la `root` réelle) calcule path/depth/numchild puis persiste
    # l'instance historique via un save() Django standard (pas Page.save()).
    root.add_child(instance=home_page)

    site = Site.objects.filter(is_default_site=True).first()
    if site:
        site.root_page_id = home_page.pk
        site.save()
    else:
        Site.objects.create(
            hostname="localhost",
            port=80,
            root_page_id=home_page.pk,
            is_default_site=True,
            site_name="Cultur'all",
        )


def remove_home_page(apps, schema_editor):
    # On cible la HomePage comme `Page` de base (via son content_type) pour ne
    # pas dépendre du modèle runtime HomePage, dont les colonnes propres
    # peuvent ne plus exister une fois 0004 annulée.
    from wagtail.models import Page, Site

    root = Page.objects.filter(depth=1).first()
    homes = Page.objects.filter(
        content_type__app_label="home", content_type__model="homepage"
    )
    for home in list(homes):
        if root is not None:
            Site.objects.filter(root_page_id=home.pk).update(root_page=root)
        home.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_contactsubmission"),
        ("wagtailcore", "0094_alter_page_locale"),
        ("wagtailsearch", "0010_add_text_fields"),
    ]

    operations = [
        migrations.RunPython(create_home_page, reverse_code=remove_home_page),
    ]
