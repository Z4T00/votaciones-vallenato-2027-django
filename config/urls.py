from django.contrib import admin
from django.urls import include, path
from votaciones import views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("votaciones.urls")),
    path("admin.html", views.panel_administracion, name="admin_home"),
    path("admin-categorias.html", views.panel_administracion),
    path("admin-votaciones.html", views.panel_administracion),
    path("admin-opciones.html", views.panel_administracion),
    path("admin-resultados.html", views.resultados, name="admin_resultados"),
]
