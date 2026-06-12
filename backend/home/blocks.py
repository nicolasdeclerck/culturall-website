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
    button = ButtonBlock()
    video = EmbedBlock(
        label="Vidéo (Vimeo, YouTube…)",
        icon="media",
        template="home/blocks/video_block.html",
    )

    class Meta:
        label = "Section personnalisable"
