from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from blog.views import article_page, blog_index
from home.auth_views import auth_check, auth_login, auth_logout
from home.views import contact_page, home_page
from pages.views import static_page_html
from projects.views import project_page, projects_index


urlpatterns = [
    # Page d'accueil rendue côté serveur : vidéo landing + projets à la une
    # + section réseau.
    path("", home_page, name="home"),

    # Authentification (sessions Django) — conservée pour le bouton Déconnexion
    # du header et un éventuel gating via require_authentication.
    path("api/auth/check/", auth_check, name="auth-check"),
    path("api/auth/login/", auth_login, name="auth-login"),
    path("api/auth/logout/", auth_logout, name="auth-logout"),

    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # Page de contact rendue côté serveur (formulaire Django + HTMX). Doit
    # précéder la route générique `<slug:slug>/` ci-dessous, sinon /contact/
    # serait interprété comme une StaticContentPage et renverrait 404.
    path("contact/", contact_page, name="contact"),

    # Blog rendu côté serveur. /blog/ = listing (+ filtre tag HTMX),
    # /blog/<slug>/ = article. Avant la route générique <slug:slug>/.
    path("blog/", blog_index, name="blog-index"),
    path("blog/<slug:slug>/", article_page, name="article-page"),

    # Projets rendus côté serveur. Mêmes contraintes d'ordre que le blog.
    path("projets/", projects_index, name="projects-index"),
    path("projets/<slug:slug>/", project_page, name="project-page"),

    # Pages statiques (À propos, Mentions légales, …) — route explicite par
    # slug, après /admin/ et avant le catch-all.
    path("<slug:slug>/", static_page_html, name="static-page-html"),

    # Catch-all Wagtail : sert nativement l'arbre de pages. Doit rester en
    # DERNIER (il matche tout).
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
