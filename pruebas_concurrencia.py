import os
import threading

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError, connection, transaction

from votaciones.models import Votacion, Voto

# Prueba CP-09: dos votos simultaneos del mismo usuario en la misma categoria.
votacion = Votacion.objects.select_related("categoria").get(pk=3)
opciones = list(votacion.opciones.filter(activa=True)[:2])

User.objects.filter(username="prueba_concurrencia").delete()
usuario = User.objects.create_user("prueba_concurrencia", password="Prueba12345")

barrera = threading.Barrier(2)
resultados = []


def votar(opcion):
    try:
        barrera.wait()
        with transaction.atomic():
            Voto.objects.create(votacion=votacion, opcion=opcion, usuario=usuario)
        resultados.append("guardado")
    except IntegrityError:
        resultados.append("rechazado por la restriccion de unicidad")
    except Exception as error:
        resultados.append(f"error: {error}")
    finally:
        connection.close()


hilos = [threading.Thread(target=votar, args=(opcion,)) for opcion in opciones]
for hilo in hilos:
    hilo.start()
for hilo in hilos:
    hilo.join()

print("Resultados:", resultados)
print("Votos guardados:", Voto.objects.filter(usuario=usuario, categoria=votacion.categoria).count())

usuario.delete()