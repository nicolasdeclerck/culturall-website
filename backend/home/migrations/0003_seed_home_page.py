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
    # Imports runtime nécessaires : la manipulation d'arbre Wagtail
    # (add_child, MP_Node) ne fonctionne qu'avec le modèle réel, pas
    # avec celui retourné par apps.get_model.
    from home.models import HomePage as RuntimeHomePage
    from wagtail.models import Page, Site

    if RuntimeHomePage.objects.exists():
        return

    root = Page.objects.filter(depth=1).first()
    if root is None:
        return

    # On ne supprime PAS la welcome page créée par le bootstrap Wagtail :
    # un Page.delete() déclenche un cascade qui interroge toutes les tables
    # liées à Page (wagtailforms, wagtailimages, etc.) et dépend d'un ordre
    # de migration cross-app difficile à garantir. On la renomme pour
    # libérer le slug "home".
    welcome = root.get_children().filter(slug="home").first()
    if welcome:
        welcome.slug = "wagtail-welcome"
        welcome.save()

    home_page = RuntimeHomePage(title="Cultur'all", slug="home")
    root.add_child(instance=home_page)
    home_page.save_revision().publish()

    site = Site.objects.filter(is_default_site=True).first()
    if site:
        site.root_page = home_page
        site.save()
    else:
        Site.objects.create(
            hostname="localhost",
            port=80,
            root_page=home_page,
            is_default_site=True,
            site_name="Cultur'all",
        )


def remove_home_page(apps, schema_editor):
    from home.models import HomePage as RuntimeHomePage
    from wagtail.models import Page, Site

    root = Page.objects.filter(depth=1).first()
    for home in list(RuntimeHomePage.objects.all()):
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
