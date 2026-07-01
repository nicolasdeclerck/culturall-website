"""
Blocs Wagtail pour la zone « Section personnalisable » de la HomePage.

Ces blocs alimentent un StreamField (cf. `HomePage.custom_section`) : depuis
l'admin Wagtail, l'éditeur empile librement titres, textes riches, images,
boutons et vidéos dans la section affichée sous « Notre Réseau ». Chaque bloc
possède son propre template de rendu dans `home/templates/home/blocks/`.
"""

from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import VideoChooserBlock

class IllustratedBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre", max_length=255)
    content = blocks.RichTextBlock(label="Contenu détaillé", required=False)
    image = ImageChooserBlock(label="Image")

    class Meta:
        icon = 'image'
        label = 'Texte illustré'
        template = 'home/blocks/illustrated_block.html'
   

class CarouselSlideBlock(blocks.StructBlock):
    """Une diapositive du carrousel : une image et une légende optionnelle."""

    image = ImageChooserBlock(label="Image")
    caption = blocks.CharBlock(label="Légende", required=False, max_length=255)

    class Meta:
        icon = "image"
        label = "Diapositive"


class CarouselBlock(blocks.StructBlock):
    """Carrousel d'images avec galerie de miniatures (« thumbs gallery »).

    Reproduit l'exemple « Thumbs gallery » de la bibliothèque SwiperJS : une
    grande image active occupe le haut du bloc ; sous elle, une bande de
    miniatures cliquables reste synchronisée avec le carrousel principal (le
    clic d'une miniature fait défiler la grande image, et inversement).
    """

    slides = blocks.ListBlock(CarouselSlideBlock(), label="Diapositives", min_num=1)

    class Meta:
        icon = "image"
        label = "Carrousel (galerie miniatures)"
        template = "home/blocks/carousel_block.html"


class KeyFigureBlock(blocks.StructBlock):
    """Un « chiffre clé » : une valeur (animée au défilement via CountUp.js) et
    son libellé, avec préfixe/suffixe optionnels (ex. « + », « % », « k »)."""

    value = blocks.DecimalBlock(
        label="Valeur",
        help_text="Le nombre vers lequel le compteur s'anime, ex. 1250 ou 98.5.",
    )
    prefix = blocks.CharBlock(
        label="Préfixe",
        required=False,
        max_length=8,
        help_text="Optionnel, affiché avant le chiffre (ex. « + », « € »).",
    )
    suffix = blocks.CharBlock(
        label="Suffixe",
        required=False,
        max_length=8,
        help_text="Optionnel, affiché après le chiffre (ex. « % », « k », « + »).",
    )
    label = blocks.CharBlock(
        label="Libellé",
        max_length=120,
        help_text="Texte affiché à droite du chiffre (ex. « bénévoles »).",
    )

    class Meta:
        icon = "decimal"
        label = "Chiffre clé"


class KeyFiguresBlock(blocks.StructBlock):
    """Section « Chiffres clés » : plusieurs chiffres empilés et décalés en
    escalier vers la droite, l'ensemble centré. Chaque chiffre s'anime (compte
    de 0 à sa valeur) à son entrée dans le viewport — cf. init dans site.js."""

    figures = blocks.ListBlock(KeyFigureBlock(), label="Chiffres", min_num=1)

    class Meta:
        icon = "decimal"
        label = "Chiffres clés"
        template = "home/blocks/key_figures_block.html"


class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(label="Texte du titre", max_length=255)

    class Meta:
        icon = "title"
        label = "Titre"
        template = "home/blocks/heading_block.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Image")
    caption = blocks.CharBlock(label="Légende", required=False, max_length=255)

    class Meta:
        icon = "image"
        label = "Image"
        template = "home/blocks/image_block.html"


class ButtonBlock(blocks.StructBlock):
    text = blocks.CharBlock(label="Libellé", max_length=80)
    url = blocks.URLBlock(label="Lien")

    class Meta:
        icon = "link"
        label = "Bouton / Lien"
        template = "home/blocks/button_block.html"


class CardBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Image", help_text="Choisie parmi les images du site.")
    title = blocks.CharBlock(label="Titre", max_length=120)
    subtitle = blocks.CharBlock(label="Sous-titre", required=False, max_length=160)
    description = blocks.TextBlock(label="Description", required=False)
    link_page = blocks.PageChooserBlock(
        label="Lien vers une page",
        required=False,
        help_text="Optionnel : rend la carte entière cliquable vers cette page du site.",
    )

    class Meta:
        icon = "form"
        label = "Carte"
        template = "home/blocks/card_block.html"


class CardGridBlock(blocks.StructBlock):
    cards = blocks.ListBlock(CardBlock(), label="Cartes", min_num=1)

    class Meta:
        icon = "grip"
        label = "Grille de cartes"
        template = "home/blocks/card_grid_block.html"


class InteractiveListItemBlock(blocks.StructBlock):
    """Un item de la « Liste interactive » : titre, détail (sous-titre + texte)
    déplié sous le titre au survol, et vidéo affichée dans le volet de droite."""

    title = blocks.CharBlock(label="Titre", max_length=120)
    subtitle = blocks.CharBlock(label="Sous-titre", required=False, max_length=200)
    content = blocks.RichTextBlock(label="Contenu détaillé", required=False)
    video = VideoChooserBlock(
        label="Vidéo",
        required=False,
        help_text=(
            "Optionnel : s'affiche dans le volet de droite au survol de l'item "
            "(sous le titre sur mobile). Fichier téléversé via « Médias »."
        ),
    )
    link_page = blocks.PageChooserBlock(
        label="Lien vers une page",
        required=False,
        help_text="Optionnel : rend l'item cliquable vers cette page du site.",
    )

    class Meta:
        icon = "doc-full"
        label = "Item de la liste"


class InteractiveListBlock(blocks.StructBlock):
    """Liste interactive à deux volets.

    Sur desktop : la liste des titres s'affiche à gauche ; au survol (ou au
    focus clavier) d'un titre, son détail (sous-titre + texte riche) se déplie
    sous le titre tandis que sa vidéo apparaît à droite avec une transition
    verticale type diaporama. Sur mobile et tablette, un appui sur le titre
    déplie tout le détail sous celui-ci (vidéo en premier, puis textes). Le
    premier item est actif par défaut.
    """

    items = blocks.ListBlock(InteractiveListItemBlock(), label="Items", min_num=1)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        # Le volet de droite (deux colonnes sur desktop) n'a de sens que si au
        # moins un item porte une vidéo ; sinon on reste sur une seule colonne
        # (détail déplié sous le titre) pour ne pas laisser un vide à droite.
        context["has_video"] = any(item.get("video") for item in value["items"])
        return context

    class Meta:
        icon = "list-ul"
        label = "Liste interactive"
        template = "home/blocks/interactive_list_block.html"


class HostedVideoBlock(blocks.StructBlock):
    """Vidéo auto-hébergée sur le site.

    L'éditeur téléverse un fichier vidéo depuis l'admin Wagtail (section
    « Médias », fournie par `wagtailmedia`) ; le fichier est stocké sur le
    MinIO du site et lu par le lecteur HTML5 natif, sans dépendre d'un service
    tiers (YouTube, Vimeo). À distinguer du bloc « Vidéo » qui, lui, *intègre*
    une vidéo hébergée ailleurs via oEmbed.
    """

    video = VideoChooserBlock(label="Fichier vidéo")
    caption = blocks.CharBlock(label="Légende", required=False, max_length=255)

    class Meta:
        icon = "wagtailmedia-video"
        label = "Vidéo hébergée"
        template = "home/blocks/hosted_video_block.html"


class AmbientVideoBlock(blocks.StructBlock):
    """Vidéo « d'ambiance » : lecture automatique, en boucle et SANS son,
    sans contrôles — typiquement en fond de section ou en bannière.

    Le son est volontairement coupé : les navigateurs n'autorisent la lecture
    automatique que sur une vidéo muette (`autoplay` impose `muted`). Comme il
    n'y a pas de contrôles, mieux vaut une vidéo courte et légère.
    """

    video = VideoChooserBlock(label="Fichier vidéo")
    loop = blocks.BooleanBlock(
        label="Lecture en boucle",
        required=False,
        default=True,
        help_text="Recommence la vidéo automatiquement à la fin (recommandé).",
    )

    class Meta:
        icon = "media"
        label = "Vidéo d'ambiance (auto, sans son)"
        template = "home/blocks/ambient_video_block.html"


class BannerBlock(blocks.StructBlock):
    """Bannière pleine largeur : une image de fond sur laquelle se superposent,
    centrés, un titre, un texte et un bouton optionnels.

    L'image est obligatoire (c'est le fond) ; titre, texte et bouton sont tous
    facultatifs. Un voile sombre est appliqué sur l'image pour garder le texte
    blanc lisible. Le bouton pointe en priorité vers une page du site
    (`button_page`), sinon vers un lien externe (`button_url`).
    """

    image = ImageChooserBlock(label="Image de fond")
    heading = blocks.CharBlock(label="Titre", required=False, max_length=255)
    text = blocks.RichTextBlock(
        label="Texte",
        required=False,
        features=["bold", "italic", "link"],
    )
    button_text = blocks.CharBlock(label="Libellé du bouton", required=False, max_length=80)
    button_page = blocks.PageChooserBlock(
        label="Bouton — lien vers une page",
        required=False,
        help_text="Optionnel : page du site visée par le bouton.",
    )
    button_url = blocks.URLBlock(
        label="Bouton — lien externe",
        required=False,
        help_text="Utilisé seulement si aucune page n'est choisie ci-dessus.",
    )

    class Meta:
        icon = "image"
        label = "Bannière"
        template = "home/blocks/banner_block.html"


class SeparatorBlock(blocks.StructBlock):
    """Espace vide vertical pour aérer le contenu. Hauteur réglable en rem."""

    height = blocks.FloatBlock(
        label="Hauteur (rem)",
        default=2,
        min_value=0,
        help_text="Hauteur de l'espace vide, en rem (1 rem ≈ 16 px).",
    )

    class Meta:
        icon = "minus"
        label = "Séparateur (espace vide)"
        template = "home/blocks/separator_block.html"


class ColumnBlock(blocks.StreamBlock):
    """Palette de blocs « simples », réutilisée telle quelle dans chaque colonne
    du bloc « 2 colonnes ». Volontairement sans le bloc « 2 colonnes » lui-même
    pour interdire toute imbrication de colonnes dans des colonnes."""

    banner = BannerBlock()
    heading = HeadingBlock()
    paragraph = blocks.RichTextBlock(
        label="Texte riche",
        icon="pilcrow",
        template="home/blocks/paragraph_block.html",
    )
    image = ImageBlock()
    card_grid = CardGridBlock()
    interactive_list = InteractiveListBlock()
    button = ButtonBlock()
    video = EmbedBlock(
        label="Vidéo (Vimeo, YouTube…)",
        icon="media",
        template="home/blocks/video_block.html",
    )
    hosted_video = HostedVideoBlock()
    ambient_video = AmbientVideoBlock()
    separator = SeparatorBlock()
    illustrated = IllustratedBlock()
    carousel = CarouselBlock()
    key_figures = KeyFiguresBlock()

    class Meta:
        label = "Colonne"


class TwoColumnBlock(blocks.StructBlock):
    """Deux colonnes côte à côte sur desktop, empilées sur mobile/tablette.

    Chaque colonne contient librement les blocs de la palette `ColumnBlock`.
    """

    left = ColumnBlock(label="Colonne de gauche", required=False)
    right = ColumnBlock(label="Colonne de droite", required=False)

    class Meta:
        icon = "grip"
        label = "2 colonnes"
        template = "home/blocks/two_column_block.html"


class CustomSectionBlock(ColumnBlock):
    """Palette de blocs proposée à l'admin dans la section personnalisable :
    tous les blocs de `ColumnBlock` plus le bloc de mise en page « 2 colonnes »."""

    two_column = TwoColumnBlock()

    class Meta:
        label = "Section personnalisable"
