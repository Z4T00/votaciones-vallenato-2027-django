# Sistema de Votaciones - Festival de la Leyenda Vallenata 2027

Proyecto de Desarrollo Web (Fundación Universitaria del Área Andina). Entrega N.º 3: módulo de votaciones, validaciones y API GET.

## Descripción

Aplicación web con Django y MySQL. Los usuarios se registran, inician sesión, eligen una categoría, seleccionan una opción y confirman su voto. El sistema permite **un solo voto por usuario, categoría y edición**; el usuario puede votar en otras categorías, consultar sus votos y los administradores revisan los registros desde Django Admin. Incluye una API GET que devuelve categorías y opciones en JSON.

## Tecnologías y versiones

- Python 3.12
- Django 5.2
- MySQL 8.0 (conector `mysqlclient` 2.3)
- Plantillas HTML y CSS de Django

## Estructura del proyecto

- `config/`: configuración del proyecto (`settings.py`, `urls.py`).
- `votaciones/`: aplicación principal (`models.py`, `views.py`, `urls.py`, `admin.py`, `migrations/`).
- `templates/` y `static/`: plantillas y estilos.
- `pruebas_concurrencia.py`: script de la prueba CP-09.

## Instalación y ejecución (Windows, PowerShell)

1. Crear la base de datos en MySQL (por ejemplo desde MySQL Workbench):

```sql
CREATE DATABASE IF NOT EXISTS votaciones_vallenato CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Crear el entorno virtual e instalar las dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Configurar la conexión a MySQL con variables de entorno, en la misma terminal. Los nombres están en `.env.example`; Django no lee ese archivo automáticamente. Usa la contraseña propia de MySQL y no la guardes en el código:

```powershell
$env:DB_ENGINE="django.db.backends.mysql"
$env:DB_NAME="votaciones_vallenato"
$env:DB_USER="root"
$env:DB_PASSWORD="TU_CONTRASENA_DE_MYSQL"
$env:DB_HOST="127.0.0.1"
```

Estas variables duran solo mientras la terminal esté abierta. Si no se define `DB_ENGINE`, el proyecto usa SQLite como respaldo local.

4. Aplicar las migraciones, crear el administrador y ejecutar el servidor:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

5. Abrir http://127.0.0.1:8000/

## Datos de prueba

Las migraciones crean la edición 2027, cuatro categorías, cuatro votaciones y dos opciones "Participante de ejemplo" por votación. Los usuarios de prueba se crean desde `/registro.html`, y el administrador con `createsuperuser`. Las opciones de ejemplo se reemplazan por las oficiales desde `/django-admin/`.

## Rutas principales

| Ruta | Descripción |
|------|-------------|
| `/` | Inicio |
| `/registro.html`, `/login.html`, `/salir/` | Registro, inicio y cierre de sesión |
| `/categorias.html` | Categorías activas |
| `/votaciones.html` | Votaciones disponibles |
| `/votar.html?id=N` | Votar (requiere sesión) |
| `/mis-votos.html` | Categorías en las que votó el usuario |
| `/api/categorias/` | API GET con categorías y opciones en JSON |
| `/django-admin/` | Administración de ediciones, categorías, votaciones, opciones y votos |
| `/admin-resultados.html` | Consulta de resultados |

## API GET

`GET /api/categorias/` devuelve las categorías activas con su edición y sus opciones, consultadas desde MySQL. Está implementada en la función `api_categorias` de `votaciones/views.py` y su ruta está en `votaciones/urls.py`. Se ejecuta de forma local con `runserver`.

## Control de duplicados

La regla de un voto por usuario, categoría y edición se garantiza en dos niveles:

- Base de datos: restricción única `un_voto_por_usuario_categoria_edicion` en el modelo `Voto` (`votaciones/models.py`, migración `0004_voto_edicion_categoria_unico.py`).
- Servidor: validación previa y manejo de `IntegrityError` en la función `votar` de `votaciones/views.py`.

## Pruebas

Las pruebas funcionales CP-01 a CP-10 se documentan en el PDF de la entrega. La prueba de concurrencia (CP-09) se ejecuta con las variables de MySQL definidas:

```powershell
.\.venv\Scripts\python.exe pruebas_concurrencia.py
```

## Seguridad

No se publican contraseñas ni credenciales. Los formularios usan protección CSRF, y el acceso a votar exige autenticación.