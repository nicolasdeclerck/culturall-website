from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls


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

    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # Catch-all Wagtail (page tree) — désactivé tant que la racine est `hello`.
    # Décommente quand un HomePage existe et retire la route `hello` ci-dessus.
    # path("", include(wagtail_urls)),
]
