from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from home.auth_views import auth_check, auth_login, auth_logout
from home.views import contact_submit
from network.views import network_member_list
from projects.views import project_list


def hello(request):
    return HttpResponse(
        "<h1>Hello, World!</h1>"
        "<p>Backend Django + Wagtail prêt. "
        "<a href='/admin/'>Wagtail admin</a> — "
        "<a href='/django-admin/'>Django admin</a></p>"
    )


urlpatterns = [
    # HelloWorld root view — à remplacer par les pages Wagtail (voir plus bas)
    # quand un HomePage aura été créé.
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

    # Catch-all Wagtail (page tree) — désactivé tant que la racine est `hello`.
    # Décommente quand un HomePage existe et retire la route `hello` ci-dessus.
    # path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
