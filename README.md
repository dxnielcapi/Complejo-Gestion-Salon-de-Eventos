# Riviera Maya · Salón de Eventos

Sistema de reservas web para complejo de eventos. Django + Tailwind CSS.

## Stack

- **Python 3.12+** · Django 6 (LTS)
- **Tailwind CSS 3** vía `django-tailwind` (compilación local con Node)
- **SQLite** en dev · PostgreSQL en prod
- Server-side rendering, sin frameworks JS de frontend

## Arranque rápido

```bash
# 1. Clonar y entrar al directorio
git clone <repo> albercas && cd albercas

# 2. Crear entorno virtual e instalar dependencias Python
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Variables de entorno (copiar y editar)
cp .env.example .env

# 4. Migrar base de datos
python manage.py migrate

# 5. Cargar datos de ejemplo
python manage.py seed_data

# 6. Instalar dependencias de Node y compilar Tailwind
cd theme/static_src
npm install
npm run build                      # build único
# — o en modo watch durante desarrollo:
# npm run start
cd ../..

# 7. Levantar servidor
python manage.py runserver
```

Abre http://127.0.0.1:8000/

## Credenciales de prueba

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Staff / Admin | `admin@rivieramaya.mx` | `admin123` |
| Cliente | `sofia.mendoza@correo.com` | `cliente123` |

## Mapa de URLs

| URL | Vista |
|-----|-------|
| `/` | Landing / Home |
| `/espacios/` | Catálogo de espacios |
| `/espacios/<slug>/` | Detalle de espacio |
| `/paquetes/` | Paquetes y servicios |
| `/disponibilidad/` | Calendario de disponibilidad |
| `/cotizar/` | Cotizador (paso 1 de 7) |
| `/cotizar/confirmacion/<codigo>/` | Confirmación |
| `/portal/reservas/` | Portal cliente — mis reservas |
| `/portal/reservas/<codigo>/` | Detalle de reserva (cliente) |
| `/ops/` | Dashboard admin |
| `/ops/agenda/` | Agenda / calendario admin |
| `/ops/reservas/` | Listado de reservas (admin) |
| `/ops/reservas/<codigo>/` | Detalle de reserva (admin) |
| `/ops/catalogo/` | Catálogo admin (espacios, paquetes, servicios) |
| `/ops/reportes/` | Reportes y métricas |
| `/accounts/login/` | Login |
| `/django-admin/` | Admin Django nativo |

## Apps

| App | Responsabilidad |
|-----|----------------|
| `core` | Landing, homepage, comando `seed_data` |
| `venues` | Modelos y vistas públicas: espacios, paquetes, disponibilidad |
| `bookings` | Wizard cotizador (sesión), confirmación, portal cliente |
| `operations` | Panel staff: dashboard, agenda, reservas, catálogo, reportes |
| `accounts` | Login/logout con Django auth |
| `theme` | App de Tailwind CSS (compilación) |

## Tailwind — desarrollo con watch

Ejecuta en dos terminales:

```bash
# Terminal 1
source venv/bin/activate && python manage.py runserver

# Terminal 2
cd theme/static_src && npm run start
```

## Migrar a PostgreSQL

1. Instalar: `pip install psycopg2-binary`
2. En `.env` configurar `DB_*` variables
3. Cambiar `DJANGO_SETTINGS_MODULE` a `riviera_maya.settings.prod`
4. `python manage.py migrate`

## Comandos útiles

```bash
python manage.py seed_data          # repoblar datos de ejemplo
python manage.py createsuperuser    # crear admin adicional
python manage.py collectstatic      # juntar estáticos para prod
```
