from django.contrib import admin
from .models import Edicion, Categoria, Votacion, Opcion, Voto

@admin.register(Edicion)
class EdicionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "anio", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre", "anio")

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "edicion", "activa")
    list_filter = ("edicion", "activa")
    search_fields = ("nombre",)

@admin.register(Votacion)
class VotacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "activa", "fecha_inicio", "fecha_fin")
    list_filter = ("activa", "categoria")
    search_fields = ("titulo",)

@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "votacion", "activa")
    list_filter = ("activa", "votacion")
    search_fields = ("nombre",)

@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("votacion", "opcion", "usuario", "creado_en")
    list_filter = ("votacion", "creado_en")
    search_fields = ("usuario__username", "opcion__nombre", "votacion__titulo")
    readonly_fields = ("votacion", "opcion", "usuario", "creado_en")
    def has_add_permission(self, request):
        return False
