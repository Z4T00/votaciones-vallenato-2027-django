```SISTEMA DE VOTACIONES - DJANGO + MYSQL

Requisitos: Python 3.12 y MySQL 8 con el servidor en ejecucion.

1. Crear la base de datos (en MySQL Workbench o en la consola de MySQL):
   CREATE DATABASE IF NOT EXISTS votaciones_vallenato CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

2. Abrir en VS Code la carpeta que contiene manage.py. En PowerShell ejecutar:
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt

3. Configurar la conexion a MySQL con variables de entorno, en la misma terminal
   (usar la contrasena propia de MySQL; no se guarda en el codigo):
   $env:DB_ENGINE="django.db.backends.mysql"
   $env:DB_NAME="votaciones_vallenato"
   $env:DB_USER="root"
   $env:DB_PASSWORD="TU_CONTRASENA_DE_MYSQL"
   $env:DB_HOST="127.0.0.1"

4. Crear las tablas, el superusuario y ejecutar el servidor:
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py createsuperuser
   .\.venv\Scripts\python.exe manage.py runserver

5. Abrir http://127.0.0.1:8000/

Notas:
- Las variables de entorno duran solo mientras la terminal este abierta.
  Hay que repetir el paso 3 cada vez que se abre una terminal nueva.
- Las migraciones cargan una edicion, categorias, votaciones y opciones de ejemplo.
- Administracion: entrar con una cuenta staff desde /login.html. El panel de Django
  esta en /django-admin/ y exige autenticacion.
- Las opciones "Participante de ejemplo" son provisionales: se reemplazan por los
  participantes oficiales desde el panel de administracion.
- Si no se define DB_ENGINE, el proyecto usa SQLite como respaldo local.```