"""Rend le menu principal administrable via l'arbre de pages Wagtail.

Le header construit désormais son menu à partir des enfants de la HomePage
cochés « Show in menus » (`show_in_menus`), via le template tag natif
`get_site_root`. Cette migration reproduit à l'identique le menu historique
(codé en dur dans `_header.html`) :

1. Crée une `ContactPage` enfant de la HomePage (slug `contact`). L'URL
   `/contact/` est servie nativement par Wagtail (formulaire + Turnstile dans
   `ContactPage.serve`).
2. Coche « Show in menus » sur Projets, À propos et Contact.
3. Réordonne ces pages pour conserver l'ordre d'affichage : Projets, À propos,
   Contact (l'ordre du menu suit l'ordre de l'arbre, réordonnable en admin).

Les manipulations d'arbre (add_child, move) et les révisions requièrent les
modèles RUNTIME (pas `apps.get_model`). La migration dépend des migrations qui
créent les pages cibles, donc toutes leurs colonnes existent déjà.
"""

from django.db import migrations

MENU_SLUGS = ["projets", "a-propos", "contact"]


def _home_page(Page):
    return Page.objects.filter(
        content_type__app_label="home", content_type__model="homepage"
    ).first()


def seed_main_menu(apps, schema_editor):
    from home.models import ContactPage
    from wagtail.models import Page

    home = _home_page(Page)
    if home is None:
        return

    # 1. Crée la ContactPage si absente (idempotent).
    contact_exists = Page.objects.filter(
        slug="contact", path__startswith=home.path
    ).exists()
    if not contact_exists:
        contact = ContactPage(
            title="Contact",
            slug="contact",
            live=True,
            show_in_menus=True,
            # locale_id explicite : évite que Page.save() résolve le parent via
            # parent.specific_class (cf. migrations de seed existantes).
            locale_id=home.locale_id,
        )
        home.add_child(instance=contact)
        contact.save_revision().publish()

    # 2. Coche « Show in menus » sur Projets et À propos. On passe par une
    # révision publiée (et pas un simple UPDATE) pour que l'état de la case
    # soit cohérent dans l'éditeur Wagtail (qui charge la dernière révision).
    for slug in ["projets", "a-propos"]:
        base = Page.objects.filter(slug=slug, path__startswith=home.path).first()
        if base is None:
            continue
        page = base.specific
        if not page.show_in_menus:
            page.show_in_menus = True
            page.save_revision().publish()

    # 3. Ordre du menu = ordre de l'arbre. On déplace chaque page de menu en
    # dernier enfant, dans l'ordre voulu, pour obtenir Projets, À propos,
    # Contact (les autres enfants — blog, mentions légales — sont hors menu).
    for slug in MENU_SLUGS:
        page = Page.objects.filter(slug=slug, path__startswith=home.path).first()
        if page is not None:
            page.move(home, pos="last-child")


def unseed_main_menu(apps, schema_editor):
    from home.models import ContactPage
    from wagtail.models import Page

    home = _home_page(Page)

    for contact in ContactPage.objects.all():
        contact.delete()

    if home is not None:
        Page.objects.filter(
            slug__in=["projets", "a-propos"], path__startswith=home.path
        ).update(show_in_menus=False)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0009_contactpage"),
        ("projects", "0008_remove_project_snippet"),
        ("pages", "0005_remove_staticpage_snippet"),
    ]

    operations = [
        migrations.RunPython(seed_main_menu, reverse_code=unseed_main_menu),
    ]
