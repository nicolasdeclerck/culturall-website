"""
Home app — point d'entrée Wagtail.

Pour l'instant ne contient qu'un HomePage minimal. Quand tu seras prêt à
basculer le routing racine sur Wagtail, lance :

    python manage.py makemigrations home
    python manage.py migrate

…puis crée une page HomePage via /admin/ et décommente la route catch-all
dans config/urls.py.
"""

from wagtail.models import Page


class HomePage(Page):
    pass
