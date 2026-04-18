# EnerFlow — Guía de Instalación

## Requisitos previos
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker + Docker Compose (opcional)

---

## Opción A — Levantar con Docker (recomendado)

```bash
# 1. Clonar / abrir la carpeta del proyecto
cd "Plataforma Operaciones"

# 2. Levantar todos los servicios
docker-compose up -d

# 3. Crear las tablas y datos iniciales
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py populate_initial_data

# 4. Acceder
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/api
# Admin Django: http://localhost:8000/admin
# Usuario: admin / Contraseña: admin123
```

---

## Opción B — Instalación manual

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Editar el archivo .env con tus datos de PostgreSQL y Redis

# Crear base de datos en PostgreSQL
# psql -U postgres -c "CREATE DATABASE enerflow_db;"

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales (tipos de documento, usuario admin)
python manage.py populate_initial_data

# Levantar servidor de desarrollo
python manage.py runserver
# API disponible en: http://localhost:8000/api
```

### Workers Celery (en terminales separadas)

```bash
# Worker
celery -A config worker -l info

# Beat scheduler (tareas programadas)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Levantar servidor de desarrollo
npm run dev
# App disponible en: http://localhost:5173
```

---

## Credenciales por defecto
- **Usuario admin:** admin
- **Contraseña:** admin123
- **Email:** admin@enerflow.co

> ⚠️ Cambiar las credenciales y el SECRET_KEY antes de producción.

---

## Estructura del proyecto

```
Plataforma Operaciones/
├── backend/                    # Django REST API
│   ├── apps/
│   │   ├── users/             # Autenticación y perfiles
│   │   ├── clientes/          # Gestión de clientes
│   │   ├── deals/             # Pipeline comercial
│   │   ├── documentos/        # Repositorio documental
│   │   ├── tareas/            # Gestión de tareas
│   │   ├── notificaciones/    # Alertas y notificaciones
│   │   └── dashboard/         # Estadísticas y KPIs
│   ├── config/                # Configuración Django
│   └── requirements.txt
├── frontend/                   # Vue 3 SPA
│   ├── src/
│   │   ├── views/             # Páginas de la app
│   │   ├── components/        # Componentes reutilizables
│   │   ├── stores/            # Estado global (Pinia)
│   │   ├── lib/               # Utilidades y API client
│   │   └── router/            # Rutas de navegación
│   └── package.json
└── docker-compose.yml
```

---

## Variables de entorno (backend/.env)

| Variable | Descripción | Default |
|---|---|---|
| SECRET_KEY | Clave secreta Django | (requerido) |
| DEBUG | Modo debug | True |
| DB_NAME | Nombre de la base de datos | enerflow_db |
| DB_USER | Usuario PostgreSQL | postgres |
| DB_PASSWORD | Contraseña PostgreSQL | (requerido) |
| DB_HOST | Host PostgreSQL | localhost |
| DB_PORT | Puerto PostgreSQL | 5432 |
| REDIS_URL | URL de Redis | redis://localhost:6379/0 |
| CORS_ALLOWED_ORIGINS | Orígenes permitidos CORS | http://localhost:5173 |

---

## API Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | /api/auth/login/ | Iniciar sesión |
| POST | /api/auth/refresh/ | Renovar token |
| GET | /api/dashboard/stats/ | KPIs del dashboard |
| GET | /api/dashboard/pipeline/ | Datos del pipeline Kanban |
| GET/POST | /api/deals/ | Listar / Crear deals |
| POST | /api/deals/{id}/cambiar-etapa/ | Cambiar etapa del deal |
| GET | /api/deals/{id}/checklist/ | Checklist de documentos |
| GET/POST | /api/clientes/ | Listar / Crear clientes |
| GET/POST | /api/documentos/ | Repositorio documental |
| GET | /api/documentos/{id}/download/ | Descargar archivo |
| GET/POST | /api/tareas/ | Gestión de tareas |
| PATCH | /api/tareas/{id}/completar/ | Marcar tarea completada |
| GET | /api/notificaciones/count/ | Conteo de no leídas |
