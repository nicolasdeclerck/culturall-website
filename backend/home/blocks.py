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
    """Un item de la « Liste interactive » : titre + détail (sous-titre + texte)."""

    title = blocks.CharBlock(label="Titre", max_length=120)
    subtitle = blocks.CharBlock(label="Sous-titre", required=False, max_length=200)
    content = blocks.RichTextBlock(label="Contenu détaillé", required=False)
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
    focus clavier) d'un titre, le détail de l'item (sous-titre + texte riche)
    apparaît à droite avec une transition verticale type diaporama. Sur mobile
    et tablette, on retombe sur une simple liste titre + sous-titre (le volet
    de droite et l'interaction au survol sont masqués).
    """

    items = blocks.ListBlock(InteractiveListItemBlock(), label="Items", min_num=1)

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


class CustomSectionBlock(blocks.StreamBlock):
    """Palette de blocs proposée à l'admin dans la section personnalisable."""

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

    class Meta:
        label = "Section personnalisable"
