from django.conf import settings
from django.db import models

class Edicion(models.Model):
    nombre = models.CharField(max_length=120)
    anio = models.PositiveSmallIntegerField(unique=True)
    activa = models.BooleanField(default=False)

    class Meta:
        ordering = ["-anio"]
        verbose_name = "edición"
        verbose_name_plural = "ediciones"

    def __str__(self):
        return f"{self.nombre} ({self.anio})"

class Categoria(models.Model):
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, related_name="categorias")
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre

class Votacion(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="votaciones")
    titulo = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["titulo"]
        verbose_name = "votación"
        verbose_name_plural = "votaciones"

    def __str__(self):
        return self.titulo

class Opcion(models.Model):
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, related_name="opciones")
    nombre = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField(blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "opción"
        verbose_name_plural = "opciones"

    def __str__(self):
        return self.nombre

class Voto(models.Model):
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, related_name="votos")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="votos")
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, related_name="votos")
    opcion = models.ForeignKey(Opcion, on_delete=models.CASCADE, related_name="votos")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votos_festival")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        constraints = [
            models.UniqueConstraint(fields=["votacion", "usuario"], name="un_voto_por_usuario_votacion"),
            models.UniqueConstraint(fields=["usuario", "categoria", "edicion"], name="un_voto_por_usuario_categoria_edicion"),
        ]
        verbose_name = "voto"
        verbose_name_plural = "votos"

    def save(self, *args, **kwargs):
        self.categoria_id = self.votacion.categoria_id
        self.edicion_id = self.votacion.categoria.edicion_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} — {self.votacion}: {self.opcion}"