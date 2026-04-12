"""Management command pour charger des données de test (articles, membres du réseau, projets).

Utilisé par le workflow de tests de non-régression afin que les tests qui ont
besoin de contenus existants (listes d'articles, projets à la une, membres du
réseau, etc.) puissent s'exécuter sans être passés sur une base vide.

La commande est idempotente : si du contenu existe déjà, on ne recrée rien
pour éviter de dupliquer les données entre deux exécutions.
"""

from __future__ import annotations

import io

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image as PILImage
from wagtail.images import get_image_model

from blog.models import Article
from network.models import NetworkMember
from projects.models import Project

WagtailImage = get_image_model()


ARTICLES = [
    {
        "title": "Lancement de la saison culturelle",
        "summary": "Un aperçu des événements phares à venir cette année.",
        "content": (
            "<p>La saison culturelle démarre avec une programmation riche et "
            "variée. Découvrez nos coups de cœur et les rendez-vous à ne pas "
            "manquer.</p><p>Concerts, expositions, ateliers : il y en aura "
            "pour tous les publics.</p>"
        ),
        "tags": ["saison", "événements"],
    },
    {
        "title": "Focus sur les artistes émergents",
        "summary": "Rencontre avec les talents qui font bouger la scène locale.",
        "content": (
            "<p>Nous mettons en lumière cinq artistes à suivre de près. "
            "Chacun développe une démarche originale, entre tradition et "
            "innovation.</p>"
        ),
        "tags": ["artistes", "portraits"],
    },
    {
        "title": "Un nouveau partenariat pour la culture",
        "summary": "Deux structures unissent leurs forces pour la scène locale.",
        "content": (
            "<p>Ce partenariat inédit va permettre de soutenir davantage de "
            "créations et de diffuser les œuvres auprès de nouveaux publics."
            "</p>"
        ),
        "tags": ["partenariats"],
    },
]

NETWORK_MEMBERS = [
    {"name": "Théâtre de la Ville", "member_type": "Salle"},
    {"name": "Collectif Arpège", "member_type": "Collectif"},
    {"name": "Festival Échos", "member_type": "Festival"},
    {"name": "Studio Nord", "member_type": "Salle"},
]

PROJECTS = [
    {
        "title": "Documentaire : Voix de la scène",
        "description": "<p>Un documentaire immersif au cœur de la scène culturelle locale.</p>",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "tags": ["documentaire", "musique"],
        "featured": True,
    },
    {
        "title": "Websérie : Les coulisses",
        "description": "<p>Une websérie qui explore l'envers du décor des créations locales.</p>",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "tags": ["websérie"],
        "featured": True,
    },
    {
        "title": "Captation du concert d'ouverture",
        "description": "<p>La captation intégrale du concert qui a lancé la saison.</p>",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "tags": ["concert", "musique"],
        "featured": True,
    },
    {
        "title": "Clip : Résonances",
        "description": "<p>Un clip tourné en partenariat avec un artiste de la scène locale.</p>",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "tags": ["clip"],
        "featured": False,
    },
]


def _generate_image_bytes(color: tuple[int, int, int], size: tuple[int, int] = (800, 500)) -> bytes:
    """Générer une petite image PNG en mémoire (Pillow est déjà requis par Wagtail)."""
    buffer = io.BytesIO()
    PILImage.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def _get_or_create_image(title: str, color: tuple[int, int, int]) -> WagtailImage:
    image = WagtailImage.objects.filter(title=title).first()
    if image:
        return image
    image = WagtailImage(title=title)
    image.file = ImageFile(io.BytesIO(_generate_image_bytes(color)), name=f"{title}.png")
    image.save()
    return image


class Command(BaseCommand):
    help = "Charge un jeu de données de test (articles, membres du réseau, projets)."

    @transaction.atomic
    def handle(self, *args, **options):
        self._seed_articles()
        self._seed_network_members()
        self._seed_projects()
        self.stdout.write(self.style.SUCCESS("Données de test chargées."))

    def _seed_articles(self) -> None:
        created = 0
        for idx, data in enumerate(ARTICLES):
            if Article.objects.filter(title=data["title"]).exists():
                continue
            illustration = _get_or_create_image(
                f"Illustration – {data['title']}",
                color=(90 + idx * 40, 120, 200 - idx * 30),
            )
            article = Article.objects.create(
                title=data["title"],
                summary=data["summary"],
                content=data["content"],
                illustration=illustration,
            )
            article.tags.add(*data["tags"])
            article.save()
            created += 1
        self.stdout.write(f"Articles : {created} créé(s), {Article.objects.count()} au total.")

    def _seed_network_members(self) -> None:
        created = 0
        for idx, data in enumerate(NETWORK_MEMBERS):
            if NetworkMember.objects.filter(name=data["name"]).exists():
                continue
            logo = _get_or_create_image(
                f"Logo – {data['name']}",
                color=(200 - idx * 40, 90 + idx * 30, 150),
            )
            NetworkMember.objects.create(
                name=data["name"],
                member_type=data["member_type"],
                logo=logo,
            )
            created += 1
        self.stdout.write(
            f"Membres du réseau : {created} créé(s), {NetworkMember.objects.count()} au total."
        )

    def _seed_projects(self) -> None:
        created = 0
        existing_featured = Project.objects.filter(featured=True).count()
        for idx, data in enumerate(PROJECTS):
            if Project.objects.filter(title=data["title"]).exists():
                continue
            thumbnail = _get_or_create_image(
                f"Miniature – {data['title']}",
                color=(150, 200 - idx * 30, 90 + idx * 40),
            )
            featured = bool(data["featured"]) and existing_featured < 3
            if featured:
                existing_featured += 1
            project = Project.objects.create(
                title=data["title"],
                description=data["description"],
                youtube_url=data["youtube_url"],
                thumbnail=thumbnail,
                featured=featured,
            )
            project.tags.add(*data["tags"])
            project.save()
            created += 1
        self.stdout.write(f"Projets : {created} créé(s), {Project.objects.count()} au total.")
