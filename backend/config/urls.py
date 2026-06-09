from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from blog.views import (
    article_detail,
    article_list,
    article_page,
    article_preview_draft,
    blog_index,
)
from home.auth_views import auth_check, auth_login, auth_logout
from home.views import contact_page, contact_submit, home_page
from network.views import network_member_list
from pages.views import static_page_detail, static_page_html, static_page_preview_draft
from projects.views import (
    project_detail,
    project_featured,
    project_list,
    project_page,
    project_preview_draft,
    projects_index,
)


urlpatterns = [
    # Page d'accueil rendue côté serveur (Phase 4) : vidéo landing + projets
    # à la une + section réseau.
    path("", home_page, name="home"),

    # API — Auth
    path("api/auth/check/", auth_check, name="auth-check"),
    path("api/auth/login/", auth_login, name="auth-login"),
    path("api/auth/logout/", auth_logout, name="auth-logout"),

    # API
    path("api/contact/", contact_submit, name="contact-submit"),

    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # API
    path("api/network/", network_member_list, name="network-member-list"),
    path("api/projects/", project_list, name="project-list"),
    path("api/projects/featured/", project_featured, name="project-featured"),
    path("api/projects/<slug:slug>/", project_detail, name="project-detail"),
    path("api/blog/articles/", article_list, name="article-list"),
    path("api/blog/articles/<slug:slug>/", article_detail, name="article-detail"),
    path("api/preview/article/", article_preview_draft, name="article-preview-draft"),
    path("api/preview/project/", project_preview_draft, name="project-preview-draft"),
    path("api/preview/page/", static_page_preview_draft, name="static-page-preview-draft"),
    path("api/pages/<slug:slug>/", static_page_detail, name="static-page-detail"),

    # Page de contact rendue côté serveur (formulaire Django + HTMX). Doit
    # précéder la route générique `<slug:slug>/` ci-dessous, sinon /contact/
    # serait interprété comme une StaticContentPage et renverrait 404.
    path("contact/", contact_page, name="contact"),

    # Blog rendu côté serveur (Phase 3). Routes explicites placées avant la
    # route générique `<slug:slug>/` (sinon /blog/ serait pris pour une page
    # statique). /blog/ = listing (+ filtre tag HTMX), /blog/<slug>/ = article.
    path("blog/", blog_index, name="blog-index"),
    path("blog/<slug:slug>/", article_page, name="article-page"),

    # Projets rendus côté serveur (Phase 4). Mêmes contraintes d'ordre que le
    # blog : avant la route générique <slug:slug>/.
    path("projets/", projects_index, name="projects-index"),
    path("projets/<slug:slug>/", project_page, name="project-page"),

    # Rendu serveur des pages statiques (À propos, Mentions légales, …) via le
    # template Wagtail natif. Route explicite par slug, placée après toutes
    # les routes /api/ et /admin/ pour ne pas les masquer.
    path("<slug:slug>/", static_page_html, name="static-page-html"),

    # Catch-all Wagtail (page tree) — RÉACTIVÉ (Phase 5a). Désormais tous les
    # templates sont en place : Wagtail sert nativement l'arbre de pages à
    # leurs URLs. Les routes explicites ci-dessus restent prioritaires (résultat
    # identique) et seront retirées en Phase 5b une fois Traefik basculé sur
    # Django. Doit rester en DERNIER (il matche tout).
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
