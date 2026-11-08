from django.db import migrations, models
import django.db.models.deletion


def llenar_edicion_categoria(apps, schema_editor):
    Voto = apps.get_model("votaciones", "Voto")
    for voto in Voto.objects.select_related("votacion__categoria"):
        voto.categoria_id = voto.votacion.categoria_id
        voto.edicion_id = voto.votacion.categoria.edicion_id
        voto.save(update_fields=["categoria", "edicion"])


class Migration(migrations.Migration):

    dependencies = [
        ("votaciones", "0003_opciones_demo"),
    ]

    operations = [
        migrations.AddField(
            model_name="voto",
            name="categoria",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="votos", to="votaciones.categoria"),
        ),
        migrations.AddField(
            model_name="voto",
            name="edicion",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="votos", to="votaciones.edicion"),
        ),
        migrations.RunPython(llenar_edicion_categoria, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="voto",
            name="categoria",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="votos", to="votaciones.categoria"),
        ),
        migrations.AlterField(
            model_name="voto",
            name="edicion",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="votos", to="votaciones.edicion"),
        ),
        migrations.AddConstraint(
            model_name="voto",
            constraint=models.UniqueConstraint(fields=("usuario", "categoria", "edicion"), name="un_voto_por_usuario_categoria_edicion"),
        ),
    ]