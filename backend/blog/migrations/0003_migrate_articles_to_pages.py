"""Migre les Articles (Snippet) vers des ArticlePages (Page Wagtail).

Étapes :
1. Crée la `BlogIndexPage` racine du blog (enfant de la `HomePage`).
2. Pour chaque `Article` existant, crée une `ArticlePage` enfant avec slug
   généré depuis le titre (collision-safe).
3. Recopie titre, résumé, contenu, illustration, tags, état brouillon,
   `first_published_at` et `last_published_at`.

La migration est idempotente : si un `ArticlePage` portant le même titre
existe déjà sous la `BlogIndexPage`, l'`Article` correspondant est ignoré.
"""

from django.db import migrations
from django.utils.text import slugify


def migrate_articles_to_pages(apps, schema_editor):
    # Idempotence : si la table source a déjà été droppée par la migration
    # successeur (0004), on no-op pour éviter un crash quand la chaîne est
    # rejouée sur une DB déjà avancée (ex : `migrate --fake` puis `migrate`
    # depuis zéro après un reset, ou cascade après InconsistentMigrationHistory).
    from django.db import connection
    if "blog_article" not in connection.introspection.table_names():
        return

    Article = apps.get_model("blog", "Article")
    ArticleTag = apps.get_model("blog", "ArticleTag")

    # La manipulation d'arbre Wagtail (add_child, MP_Node) requiert les
    # modèles runtime, pas ceux retournés par apps.get_model.
    from blog.models import ArticlePage as RuntimeArticlePage
    from blog.models import BlogIndexPage as RuntimeBlogIndexPage
    from home.models import HomePage as RuntimeHomePage

    home = RuntimeHomePage.objects.first()
    if home is None:
        return

    blog_index = RuntimeBlogIndexPage.objects.descendant_of(home).first()
    if blog_index is None:
        blog_index = RuntimeBlogIndexPage(title="Blog", slug="blog")
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()

    existing_slugs = set(blog_index.get_children().values_list("slug", flat=True))

    for article in Article.objects.all().order_by("created_at"):
        if (
            RuntimeArticlePage.objects.descendant_of(blog_index)
            .filter(title=article.title)
            .exists()
        ):
            continue

        base_slug = slugify(article.title) or "article"
        slug = base_slug
        suffix = 2
        while slug in existing_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        existing_slugs.add(slug)

        article_page = RuntimeArticlePage(
            title=article.title,
            slug=slug,
            summary=article.summary,
            content=article.content,
            # On passe l'ID, pas l'instance : `article.illustration` est une
            # instance du modèle historique de wagtailimages.Image (récupéré
            # via apps.get_model), incompatible avec le FK de ArticlePage qui
            # attend le modèle runtime. Même table en base, classes Python
            # distinctes.
            illustration_id=article.illustration_id,
            live=article.live,
            has_unpublished_changes=article.has_unpublished_changes,
            first_published_at=article.first_published_at or article.created_at,
            last_published_at=article.last_published_at or article.updated_at,
        )
        blog_index.add_child(instance=article_page)

        tag_names = list(
            ArticleTag.objects.filter(content_object=article)
            .values_list("tag__name", flat=True)
        )
        if tag_names:
            article_page.tags.add(*tag_names)
            article_page.save()


def reverse_migrate(apps, schema_editor):
    from blog.models import ArticlePage as RuntimeArticlePage
    from blog.models import BlogIndexPage as RuntimeBlogIndexPage

    for page in list(RuntimeArticlePage.objects.all()):
        page.delete()
    for page in list(RuntimeBlogIndexPage.objects.all()):
        page.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_create_pages"),
        ("home", "0003_seed_home_page"),
    ]

    operations = [
        migrations.RunPython(migrate_articles_to_pages, reverse_code=reverse_migrate),
    ]
