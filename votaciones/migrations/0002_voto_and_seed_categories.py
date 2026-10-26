import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def seed_categories(apps, schema_editor):
    Edicion = apps.get_model('votaciones', 'Edicion')
    Categoria = apps.get_model('votaciones', 'Categoria')
    Votacion = apps.get_model('votaciones', 'Votacion')
    edicion, _ = Edicion.objects.get_or_create(
        anio=2027,
        defaults={'nombre': 'Festival de la Leyenda Vallenata', 'activa': True},
    )
    data = [
        ('Rey Vallenato Profesional', 'Concurso para elegir al Rey Vallenato en la categoría profesional.', 'Elección del Rey Vallenato Profesional 2027'),
        ('Rey Aficionado', 'Ejecutantes que mantienen viva la tradición fuera del escenario profesional.', 'Final Rey Aficionado'),
        ('Rey Juvenil', 'Nuevos talentos del acordeón, la caja y la guacharaca.', 'Final Rey Juvenil'),
        ('Canción Inédita', 'Composiciones nuevas que aún no se han grabado ni publicado.', 'Premio Canción Inédita'),
    ]
    for nombre, descripcion, titulo in data:
        categoria, _ = Categoria.objects.get_or_create(
            edicion=edicion, nombre=nombre,
            defaults={'descripcion': descripcion, 'activa': True},
        )
        Votacion.objects.get_or_create(
            categoria=categoria, titulo=titulo,
            defaults={'descripcion': f'Votación correspondiente a {nombre} para la edición 2027.', 'activa': True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('votaciones', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Voto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('opcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votos', to='votaciones.opcion')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votos_festival', to=settings.AUTH_USER_MODEL)),
                ('votacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votos', to='votaciones.votacion')),
            ],
            options={'verbose_name': 'voto', 'verbose_name_plural': 'votos', 'ordering': ['-creado_en']},
        ),
        migrations.AddConstraint(
            model_name='voto',
            constraint=models.UniqueConstraint(fields=('votacion', 'usuario'), name='un_voto_por_usuario_votacion'),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
