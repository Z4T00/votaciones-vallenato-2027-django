from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("index.html", views.inicio, name="inicio_html"),
    path("categorias.html", views.categorias, name="categorias"),
    path("votaciones.html", views.votaciones, name="votaciones"),
    path("votar.html", views.votar, name="votar"),
    path("confirmacion.html", views.confirmacion, name="confirmacion"),
    path("resultado.html", views.resultados, name="resultados"),
    path("login.html", views.iniciar_sesion, name="login"),
    path("registro.html", views.registro, name="registro"),
    path("salir/", views.cerrar_sesion, name="logout"),
]
