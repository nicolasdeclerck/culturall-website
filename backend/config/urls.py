from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from home.auth_views import auth_check, auth_login, auth_logout


urlpatterns = [
    # Authentification (sessions Django) — conservée pour le bouton Déconnexion
    # du header et le gating éventuel via require_authentication.
    path("api/auth/check/", auth_check, name="auth-check"),
    path("api/auth/login/", auth_login, name="auth-login"),
    path("api/auth/logout/", auth_logout, name="auth-logout"),

    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),

    # Wagtail sert nativement l'intégralité de l'arbre de pages : accueil (/),
    # projets, blog, pages statiques (À propos, Mentions légales) et contact.
    # Chaque page se rend via son template + `get_context` (et `serve()` pour
    # la soumission du formulaire de contact). Doit rester en DERNIER : ce
    # catch-all matche tout.
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
