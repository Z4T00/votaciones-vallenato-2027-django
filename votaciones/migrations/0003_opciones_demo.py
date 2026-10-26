from django.db import migrations


def seed_demo_options(apps, schema_editor):
    Votacion = apps.get_model("votaciones", "Votacion")
    Opcion = apps.get_model("votaciones", "Opcion")
    for votacion in Votacion.objects.filter(activa=True):
        # Opciones de demostración para que cada categoría pueda probarse.
        # El administrador debe sustituirlas por los participantes oficiales.
        Opcion.objects.get_or_create(
            votacion=votacion,
            nombre="Participante de ejemplo 1",
            defaults={"descripcion": "Opción provisional de demostración.", "activa": True},
        )
        Opcion.objects.get_or_create(
            votacion=votacion,
            nombre="Participante de ejemplo 2",
            defaults={"descripcion": "Opción provisional de demostración.", "activa": True},
        )


class Migration(migrations.Migration):
    dependencies = [("votaciones", "0002_voto_and_seed_categories")]
    operations = [migrations.RunPython(seed_demo_options, migrations.RunPython.noop)]
