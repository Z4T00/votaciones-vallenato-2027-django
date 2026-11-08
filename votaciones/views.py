from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Categoria, Edicion, Opcion, Votacion, Voto


def pagina(request, nombre):
    return render(request, nombre)


def inicio(request):
    return render(request, "index.html")


def categorias(request):
    qs = Categoria.objects.filter(activa=True, edicion__activa=True).select_related("edicion")
    return render(request, "categorias.html", {"categorias": qs})


def votaciones(request):
    qs = Votacion.objects.filter(activa=True, categoria__activa=True, categoria__edicion__activa=True).select_related("categoria")
    categoria_id = request.GET.get("categoria")
    if categoria_id and categoria_id.isdigit():
        qs = qs.filter(categoria_id=int(categoria_id))
    ahora = timezone.now()
    items = []
    for votacion in qs:
        abierta = (votacion.fecha_inicio is None or votacion.fecha_inicio <= ahora) and (votacion.fecha_fin is None or votacion.fecha_fin >= ahora)
        items.append({"obj": votacion, "abierta": abierta, "ya_voto": request.user.is_authenticated and Voto.objects.filter(categoria_id=votacion.categoria_id, edicion_id=votacion.categoria.edicion_id, usuario=request.user).exists(), "tiene_opciones": votacion.opciones.filter(activa=True).exists()})
    return render(request, "votaciones.html", {"votaciones_lista": items})


def votar(request):
    votacion_id = request.GET.get("id") or request.POST.get("votacion_id")
    if not str(votacion_id).isdigit():
        messages.error(request, "Votación no válida.")
        return redirect("votaciones")
    if not request.user.is_authenticated:
        messages.info(request, "Inicia sesión para registrar tu voto.")
        return redirect(f"/login.html?next=/votar.html?id={votacion_id}")
    votacion = get_object_or_404(Votacion.objects.select_related("categoria", "categoria__edicion"), pk=votacion_id)
    categoria = votacion.categoria
    edicion = categoria.edicion
    if not (votacion.activa and categoria.activa and edicion.activa):
        messages.error(request, "Esta categoría no está habilitada para votar.")
        return redirect("votaciones")
    ahora = timezone.now()
    if (votacion.fecha_inicio and votacion.fecha_inicio > ahora) or (votacion.fecha_fin and votacion.fecha_fin < ahora):
        messages.error(request, "Esta votación no está abierta en este momento.")
        return redirect("votaciones")
    if Voto.objects.filter(usuario=request.user, categoria=categoria, edicion=edicion).exists():
        messages.warning(request, "Ya votaste en esta categoría. Solo se permite un voto por categoría en cada edición.")
        return redirect("votaciones")
    opciones = votacion.opciones.filter(activa=True)
    if request.method == "POST":
        opcion_id = request.POST.get("opcion", "")
        opcion = opciones.filter(pk=opcion_id).first() if opcion_id.isdigit() else None
        if opcion is None:
            messages.error(request, "La opción seleccionada no es válida para esta votación.")
            return redirect(f"/votar.html?id={votacion.id}")
        try:
            with transaction.atomic():
                Voto.objects.create(votacion=votacion, opcion=opcion, usuario=request.user)
        except IntegrityError:
            messages.warning(request, "Ya votaste en esta categoría. Solo se permite un voto por categoría en cada edición.")
            return redirect("votaciones")
        request.session["ultimo_voto"] = {"votacion": votacion.titulo, "opcion": opcion.nombre}
        return redirect("confirmacion")
    return render(request, "votar.html", {"votacion": votacion, "opciones": opciones})


def confirmacion(request):
    return render(request, "confirmacion.html", {"ultimo_voto": request.session.get("ultimo_voto")})


def resultados(request):
    votaciones_qs = Votacion.objects.filter(activa=True).select_related("categoria")
    seleccion = request.GET.get("votacion")
    votacion = get_object_or_404(votaciones_qs, pk=seleccion) if seleccion and seleccion.isdigit() else votaciones_qs.first()
    filas = []
    total = 0
    if votacion:
        opciones = votacion.opciones.annotate(total_votos=Count("votos")).order_by("-total_votos", "nombre")
        total = sum(o.total_votos for o in opciones)
        for opcion in opciones:
            filas.append({"opcion": opcion, "votos": opcion.total_votos, "porcentaje": round(opcion.total_votos * 100 / total, 1) if total else 0})
    return render(request, "admin-resultados.html", {"votaciones_lista": votaciones_qs, "votacion_seleccionada": votacion, "filas_resultados": filas, "total_votos": total})


def iniciar_sesion(request):
    siguiente = request.GET.get("next") or request.POST.get("next") or "/categorias.html"
    if request.method == "POST":
        identificador = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        usuario = authenticate(request, username=identificador, password=password)
        if usuario is None and "@" in identificador:
            coincidencia = User.objects.filter(email__iexact=identificador).first()
            if coincidencia:
                usuario = authenticate(request, username=coincidencia.username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect(siguiente if siguiente.startswith("/") and not siguiente.startswith("//") else "/categorias.html")
        messages.error(request, "Usuario/correo o contraseña incorrectos.")
    return render(request, "login.html", {"next_url": siguiente})


def registro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip().lower()
        username = request.POST.get("username", "").strip() or email
        password = request.POST.get("password", "")
        confirmacion_password = request.POST.get("confirmar_password", "")
        if not nombre or not email or not password:
            messages.error(request, "Completa todos los campos obligatorios.")
        elif password != confirmacion_password:
            messages.error(request, "Las contraseñas no coinciden.")
        elif User.objects.filter(email__iexact=email).exists() or User.objects.filter(username=username).exists():
            messages.error(request, "Ya existe una cuenta con ese correo o usuario.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=nombre)
            login(request, user)
            messages.success(request, "Tu cuenta fue creada correctamente.")
            return redirect("categorias")
    return render(request, "registro.html")


def cerrar_sesion(request):
    logout(request)
    return redirect("inicio")


@staff_member_required(login_url="/login.html")
def panel_administracion(request):
    return render(request, "admin.html")

@login_required(login_url="/login.html")
def mis_votos(request):
    votos = Voto.objects.filter(usuario=request.user).select_related("edicion", "categoria", "votacion", "opcion")
    return render(request, "mis_votos.html", {"votos": votos})

@require_GET
def api_categorias(request):
    categorias = (
        Categoria.objects.filter(activa=True, edicion__activa=True)
        .select_related("edicion")
        .prefetch_related("votaciones__opciones")
    )
    datos = []
    for categoria in categorias:
        opciones = []
        for votacion in categoria.votaciones.all():
            if not votacion.activa:
                continue
            for opcion in votacion.opciones.all():
                if opcion.activa:
                    opciones.append({
                        "id": opcion.id,
                        "nombre": opcion.nombre,
                        "descripcion": opcion.descripcion,
                        "votacion_id": votacion.id,
                        "votacion": votacion.titulo,
                    })
        datos.append({
            "id": categoria.id,
            "nombre": categoria.nombre,
            "descripcion": categoria.descripcion,
            "edicion": {"id": categoria.edicion.id, "nombre": categoria.edicion.nombre, "anio": categoria.edicion.anio},
            "opciones": opciones,
        })
    return JsonResponse({"categorias": datos}, json_dumps_params={"ensure_ascii": False, "indent": 2})