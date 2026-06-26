# Ajouter un bloc sélectionnable dans les sections personnalisables

Guide pratique pour ajouter un nouveau type de bloc à la zone « Section
personnalisable » de la page d'accueil (`HomePage`).

---

## TL;DR

Les sections personnalisables sont des **StreamField Wagtail**. Un « bloc
sélectionnable » est une classe Python (héritant de `StructBlock`) déclarée
dans [backend/home/blocks.py](../backend/home/blocks.py), exposée à l'éditeur en
l'ajoutant comme attribut d'un `StreamBlock`, et rendue via un template HTML.

Pour ajouter un bloc, on touche **4 endroits** (+ 1 migration auto-générée) :

| # | Fichier | Action |
|---|---------|--------|
| 1 | [backend/home/blocks.py](../backend/home/blocks.py) | Définir la classe du bloc |
| 2 | [backend/home/blocks.py](../backend/home/blocks.py) | L'ajouter à `ColumnBlock` ou `CustomSectionBlock` |
| 3 | `backend/home/templates/home/blocks/<mon_bloc>.html` | Créer le template de rendu |
| 4 | [backend/static/css/main.css](../backend/static/css/main.css) | Ajouter les styles |
| 5 | _(auto)_ | `python manage.py makemigrations home` |

On ne touche **ni** `models.py`, **ni** `home_page.html`, **ni** l'admin : le
StreamField reste `CustomSectionBlock()` et le rendu est dynamique.

---

## Comment ça marche

### L'architecture

```
HomePage  (backend/home/models.py)
├─ top_custom_section : StreamField(CustomSectionBlock())   ← au-dessus du réseau
└─ custom_section     : StreamField(CustomSectionBlock())   ← sous le réseau
```

Chaque section est une **pile de blocs** composée librement par l'éditeur depuis
l'admin Wagtail, sérialisée en JSON dans la base de données.

### La palette de blocs (`backend/home/blocks.py`)

Deux `StreamBlock` définissent ce que l'éditeur peut empiler :

- **`ColumnBlock`** — la palette « simple » (titre, texte, image, carte, vidéo,
  bannière, séparateur…). Volontairement **sans** le bloc « 2 colonnes » pour
  interdire l'imbrication de colonnes dans des colonnes. C'est aussi cette
  palette qui est proposée à l'intérieur de chaque colonne du bloc 2 colonnes.
- **`CustomSectionBlock`** — hérite de `ColumnBlock` et y ajoute `two_column`.
  C'est la palette complète proposée dans les deux sections personnalisables.

```python
class CustomSectionBlock(ColumnBlock):
    two_column = TwoColumnBlock()

    class Meta:
        label = "Section personnalisable"
```

> Comme `CustomSectionBlock` **hérite** de `ColumnBlock`, un bloc ajouté à
> `ColumnBlock` apparaît automatiquement dans les sections personnalisables **et**
> dans les colonnes du bloc 2 colonnes. À l'inverse, un bloc ajouté seulement à
> `CustomSectionBlock` n'est disponible qu'au niveau racine des sections (pas dans
> une colonne).

### Le rendu (`home_page.html`)

Le template parcourt la pile et délègue le rendu à Wagtail :

```django
{% for block in page.custom_section %}
  {% include_block block %}
{% endfor %}
```

`{% include_block %}` lit le type du bloc et rend le template déclaré dans sa
`class Meta.template`. **Aucun mapping manuel** type → template à maintenir.

---

## Pas à pas : ajouter un bloc

Exemple : un bloc « Témoignage » (citation + auteur + fonction).

### 1. Définir la classe du bloc

Dans [backend/home/blocks.py](../backend/home/blocks.py), avant `ColumnBlock` :

```python
class TestimonialBlock(blocks.StructBlock):
    """Bloc témoignage : citation, nom de l'auteur, fonction, photo optionnelle."""

    quote = blocks.TextBlock(label="Citation", max_length=500)
    author_name = blocks.CharBlock(label="Nom de l'auteur", max_length=100)
    author_role = blocks.CharBlock(label="Fonction", required=False, max_length=150)
    author_photo = ImageChooserBlock(label="Photo de l'auteur", required=False)

    class Meta:
        icon = "user"                               # icône Wagtail
        label = "Témoignage"                        # libellé dans l'éditeur
        template = "home/blocks/testimonial_block.html"
```

Conventions du fichier (cf. blocs existants) :
- hériter de `blocks.StructBlock` (ou `blocks.StreamBlock` si le bloc en contient
  d'autres, comme `ColumnBlock`) ;
- libeller chaque champ en français via `label=...`, marquer l'optionnel avec
  `required=False`, et utiliser `help_text=...` pour guider l'éditeur ;
- une docstring expliquant le rôle et le comportement du bloc ;
- `Meta.template` pointe vers `home/blocks/<nom>.html` ;
- types de champs utiles déjà importés en tête de fichier :
  `ImageChooserBlock` (images du site), `VideoChooserBlock` (fichiers Médias /
  wagtailmedia), `EmbedBlock` (oEmbed YouTube/Vimeo), `blocks.RichTextBlock`,
  `blocks.PageChooserBlock` (lien vers une page du site), `blocks.ListBlock`.

### 2. L'ajouter à la palette

Pour le rendre disponible **partout** (sections + colonnes), l'ajouter à
`ColumnBlock` :

```python
class ColumnBlock(blocks.StreamBlock):
    banner = BannerBlock()
    heading = HeadingBlock()
    # ... blocs existants ...
    separator = SeparatorBlock()
    testimonial = TestimonialBlock()   # ← ajout

    class Meta:
        label = "Colonne"
```

Pour le réserver **au niveau racine** des sections (pas dans une colonne),
l'ajouter plutôt à `CustomSectionBlock` :

```python
class CustomSectionBlock(ColumnBlock):
    two_column = TwoColumnBlock()
    testimonial = TestimonialBlock()   # ← ajout réservé à la racine

    class Meta:
        label = "Section personnalisable"
```

> La clé de l'attribut (`testimonial`) devient le `type` stocké en base. Évite
> de la renommer après coup : du contenu déjà saisi y serait rattaché.

### 3. Créer le template de rendu

Nouveau fichier `backend/home/templates/home/blocks/testimonial_block.html` :

```django
{% load wagtailcore_tags wagtailimages_tags %}
{% comment %}Bloc témoignage : citation + auteur + fonction.{% endcomment %}
<blockquote class="custom-testimonial">
  <p class="custom-testimonial__quote">{{ self.quote }}</p>
  <footer class="custom-testimonial__footer">
    {% if self.author_photo %}
      {% image self.author_photo width-120 class="custom-testimonial__photo" %}
    {% endif %}
    <div class="custom-testimonial__author">
      <strong class="custom-testimonial__name">{{ self.author_name }}</strong>
      {% if self.author_role %}
        <em class="custom-testimonial__role">{{ self.author_role }}</em>
      {% endif %}
    </div>
  </footer>
</blockquote>
```

Conventions de template :
- accéder aux champs via `{{ self.<champ> }}` ;
- images via `{% image %}` (`wagtailimages_tags`), texte riche via le filtre
  `|richtext` (`wagtailcore_tags`), sous-blocs via `{% include_block %}` ;
- une classe CSS racine en `custom-<nom>` avec ses enfants en BEM
  (`custom-<nom>__<élément>`), comme `.custom-card`, `.custom-banner`, `.ilist` ;
- pas de style inline : tout le style va dans `main.css`.

### 4. Ajouter les styles

Dans [backend/static/css/main.css](../backend/static/css/main.css), à la suite
des autres styles `.custom-*` (section « custom-section ») :

```css
.custom-testimonial {
  margin: 2rem 0;
  padding: 1.5rem;
  border-left: 4px solid var(--primary-color);
}
.custom-testimonial__quote { font-style: italic; font-size: 1.125rem; }
.custom-testimonial__footer { display: flex; gap: 1rem; align-items: center; }
.custom-testimonial__photo { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; }
.custom-testimonial__author { display: flex; flex-direction: column; }
```

Réutilise les variables CSS du projet (`var(--…)`) et pense au responsive
(mobile/tablette) comme les blocs existants.

### 5. Générer la migration

Modifier un StreamField change sa définition sérialisée → Wagtail veut une
migration :

```bash
cd backend
python manage.py makemigrations home
python manage.py migrate
```

La migration est **auto-générée** (elle met à jour le `block_lookup` des deux
champs). Ne pas l'éditer à la main, ne pas modifier les migrations existantes.

---

## Vérifier

1. Lancer le backend, ouvrir l'admin Wagtail → page d'accueil.
2. Dans « Section personnalisable », cliquer pour ajouter un bloc : « Témoignage »
   apparaît dans la liste avec son icône et son libellé.
3. Remplir un bloc, **enregistrer en brouillon**, prévisualiser → le HTML rendu
   et le style s'affichent correctement.

---

## Référence des blocs existants

| Type (clé) | Classe | Template |
|---|---|---|
| `heading` | `HeadingBlock` | `heading_block.html` |
| `paragraph` | `RichTextBlock` (inline) | `paragraph_block.html` |
| `image` | `ImageBlock` | `image_block.html` |
| `button` | `ButtonBlock` | `button_block.html` |
| `card_grid` | `CardGridBlock` (→ `CardBlock`) | `card_grid_block.html` |
| `interactive_list` | `InteractiveListBlock` (→ `InteractiveListItemBlock`) | `interactive_list_block.html` |
| `banner` | `BannerBlock` | `banner_block.html` |
| `video` | `EmbedBlock` (inline, oEmbed) | `video_block.html` |
| `hosted_video` | `HostedVideoBlock` | `hosted_video_block.html` |
| `ambient_video` | `AmbientVideoBlock` | `ambient_video_block.html` |
| `separator` | `SeparatorBlock` | `separator_block.html` |
| `two_column` | `TwoColumnBlock` (→ `ColumnBlock` ×2) | `two_column_block.html` |

Fichiers de référence :
[blocks.py](../backend/home/blocks.py) ·
[models.py](../backend/home/models.py) ·
[home_page.html](../backend/home/templates/home/home_page.html) ·
[templates/home/blocks/](../backend/home/templates/home/blocks/) ·
[main.css](../backend/static/css/main.css)
