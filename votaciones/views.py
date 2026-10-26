from django.contrib import messages
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
        items.append({"obj": votacion, "abierta": abierta, "ya_voto": request.user.is_authenticated and Voto.objects.filter(votacion=votacion, usuario=request.user).exists(), "tiene_opciones": votacion.opciones.filter(activa=True).exists()})
    return render(request, "votaciones.html", {"votaciones_lista": items})


def votar(request):
    votacion_id = request.GET.get("id") or request.POST.get("votacion_id")
    votacion = get_object_or_404(Votacion.objects.select_related("categoria", "categoria__edicion"), pk=votacion_id, activa=True, categoria__activa=True, categoria__edicion__activa=True)
    ahora = timezone.now()
    if (votacion.fecha_inicio and votacion.fecha_inicio > ahora) or (votacion.fecha_fin and votacion.fecha_fin < ahora):
        messages.error(request, "Esta votación no está abierta en este momento.")
        return redirect("votaciones")
    if not request.user.is_authenticated:
        messages.info(request, "Inicia sesión para registrar tu voto.")
        return redirect(f"/login.html?next=/votar.html?id={votacion.id}")
    if Voto.objects.filter(votacion=votacion, usuario=request.user).exists():
        messages.warning(request, "Ya registraste un voto en esta votación.")
        return redirect("votaciones")
    opciones = votacion.opciones.filter(activa=True)
    if request.method == "POST":
        opcion = get_object_or_404(opciones, pk=request.POST.get("opcion"))
        try:
            with transaction.atomic():
                Voto.objects.create(votacion=votacion, opcion=opcion, usuario=request.user)
        except IntegrityError:
            messages.warning(request, "Ya registraste un voto en esta votación.")
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
