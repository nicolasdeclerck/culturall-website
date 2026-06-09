from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
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
from home.views import contact_page, contact_submit
from network.views import network_member_list
from pages.views import static_page_detail, static_page_html, static_page_preview_draft
from projects.views import project_detail, project_featured, project_list, project_preview_draft


def hello(request):
    return HttpResponse(
        "<h1>Hello, World!</h1>"
        "<p>Backend Django + Wagtail prêt. "
        "<a href='/admin/'>Wagtail admin</a> — "
        "<a href='/django-admin/'>Django admin</a></p>"
    )


urlpatterns = [
    # HelloWorld root view — le backend est headless, le rendu HTML est fait
    # par Next.js. Le catch-all Wagtail (plus bas) reste désactivé tant qu'on
    # n'a pas câblé wagtail-headless-preview (#121).
    path("", hello),

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

    # Rendu serveur des pages statiques (À propos, Mentions légales, …) via le
    # template Wagtail natif. Route explicite par slug : on ne réactive PAS
    # encore le catch-all Wagtail global (Phase 5) pour ne pas exposer les
    # pages blog/projets/home qui n'ont pas encore de template. Placée après
    # toutes les routes /api/ et /admin/ pour ne pas les masquer.
    path("<slug:slug>/", static_page_html, name="static-page-html"),

    # Catch-all Wagtail (page tree) — désactivé : Next.js gère encore le rendu
    # des sections non migrées. Réactivation prévue en Phase 5 (bascule
    # monolithe), une fois tous les templates en place.
    # path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
