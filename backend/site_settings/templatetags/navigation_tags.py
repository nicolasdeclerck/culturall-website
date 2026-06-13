"""Tags de navigation natifs Wagtail.

Le menu principal est construit à partir de l'arbre de pages : on itère sur
les enfants live du root page du site qui ont la case « Show in menus »
(`show_in_menus`) cochée dans l'onglet *Promote* de l'admin. C'est l'approche
décrite par le tutoriel Wagtail (« Set up a site menu »).
"""

from django import template
from wagtail.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_root(context):
    """Retourne le root page du site courant (parent des entrées de menu).

    Renvoie ``None`` si la requête n'est pas disponible ou si aucun site ne
    correspond, afin que le template puisse dégrader proprement.
    """
    request = context.get("request")
    if request is None:
        return None
    site = Site.find_for_request(request)
    return site.root_page if site else None
