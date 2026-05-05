from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from blog.views import article_detail, article_list, article_preview_draft
from home.auth_views import auth_check, auth_login, auth_logout
from home.views import contact_submit
from network.views import network_member_list
from pages.views import static_page_detail
from projects.views import project_detail, project_featured, project_list


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
    path("api/preview/draft/", article_preview_draft, name="article-preview-draft"),
    path("api/pages/<slug:slug>/", static_page_detail, name="static-page-detail"),

    # Catch-all Wagtail (page tree) — désactivé : on est headless, Next.js
    # gère le rendu. À activer quand on installera wagtail-headless-preview
    # (#121) pour que la preview rédactionnelle puisse pointer ici.
    # path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
