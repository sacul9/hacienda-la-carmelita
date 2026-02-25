# Hacienda La Carmelita — Plataforma Digital

> Turismo rural premium en Lérida, Tolima, Colombia
> Origen del Arroz Colombiano

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | Nuxt 3 + Vue.js + Tailwind CSS |
| Backend | FastAPI + Python 3.12 |
| Base de datos | PostgreSQL 16 (Supabase) |
| Caché / Queue | Redis (Upstash) |
| Tareas async | Celery |
| Pagos CO | Wompi |
| Pagos INT | Stripe |
| SMS / WhatsApp | Twilio |
| Email | SendGrid |
| IA | Claude API (Anthropic) |
| Deploy FE | Vercel |
| Deploy BE | Railway |
| CDN / WAF | Cloudflare |

---

## Setup Local

### Requisitos previos

- Docker Desktop 4.x+
- Node.js 20+
- Python 3.12+
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-org/hacienda-la-carmelita.git
cd hacienda-la-carmelita
```

### 2. Configurar variables de entorno

```bash
# Backend
cp backend/.env.example backend/.env
# Edita backend/.env con tus credenciales reales

# Frontend
cp frontend/.env.example frontend/.env
# Edita frontend/.env con tus keys públicas
```

### 3. Levantar con Docker Compose

```bash
# Levantar PostgreSQL + Redis + Backend + Frontend
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f backend
docker-compose logs -f frontend

# Levantar con workers Celery también
docker-compose --profile full up -d
```

### 4. Verificar que todo funciona

```bash
# Backend health check
curl http://localhost:8000/health
# → {"status": "ok", "app": "Hacienda La Carmelita API", ...}

# Frontend
open http://localhost:3000
```

---

## Desarrollo sin Docker

### Backend

```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Copiar y configurar .env
cp .env.example .env

# Ejecutar en modo desarrollo
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
# → http://localhost:3000
```

---

## Tests

### Backend

```bash
cd backend
pytest                          # Todos los tests
pytest tests/test_otp.py        # Solo tests de OTP
pytest --cov=app                # Con reporte de cobertura
```

### Frontend

```bash
cd frontend
npm run test                    # Tests unitarios (Vitest)
npm run test:coverage           # Con reporte de cobertura
```

---

## Estructura del Proyecto

```
hacienda-la-carmelita/
├── frontend/                   # Nuxt 3 PWA
│   ├── pages/                  # Rutas del sitio
│   ├── components/             # Componentes Vue
│   ├── stores/                 # Pinia (estado global)
│   ├── composables/            # Lógica reutilizable
│   └── locales/                # Traducciones ES/EN
│
├── backend/                    # FastAPI
│   ├── app/
│   │   ├── models/             # SQLModel (9 tablas)
│   │   ├── routers/            # Endpoints de la API
│   │   ├── auth/               # JWT + OTP
│   │   ├── agents/             # Agentes de IA
│   │   └── notificaciones/     # Email + WhatsApp
│   ├── workers/                # Celery workers
│   └── tests/                  # Pytest
│
├── docs/                       # Documentación técnica
├── scripts/                    # Scripts SQL y utilidades
├── .github/workflows/          # CI/CD GitHub Actions
└── docker-compose.yml          # Stack de desarrollo local
```

---

## Roadmap de Sprints

| Sprint | Semana | Módulo |
|--------|--------|--------|
| Sprint 0 | 1 | Infraestructura + Setup |
| Sprint 1 | 2 | Auth + OTP (3 canales) |
| Sprint 2 | 3-4 | Motor de Reservas |
| Sprint 3 | 5-6 | Pagos Wompi + Stripe |
| Sprint 4 | 7 | Notificaciones |
| Sprint 5 | 8 | Landing Page |
| Sprint 6 | 9 | Panel Admin |
| Sprint 7 | 10-11 | Channel Manager |
| Sprint 8 | 12-13 | Agentes IA |
| Sprint 9 | 14 | PWA + Performance |
| Sprint 10 | 15-16 | QA Final + Producción |

---

## Variables de Entorno Requeridas

Todas las variables están documentadas en:
- `backend/.env.example`
- `frontend/.env.example`

**NUNCA** commitear archivos `.env` con credenciales reales.
Usar **Doppler** para gestión de secretos en producción.

---

## Seguridad

- JWT con TTL de 15 minutos + refresh token en httpOnly cookie
- OTP de 6 dígitos con hash SHA-256, TTL 10 min, máx 3 intentos
- Rate limiting en endpoints sensibles (Redis)
- 2FA obligatorio para acceso al panel de admin
- NUNCA se almacenan datos de tarjeta (solo tokens de Wompi/Stripe)
- Headers de seguridad: CSP, HSTS, X-Frame-Options, nosniff

---

## Equipo

| Rol | Nombre |
|-----|--------|
| CTO | Sergio Luna |
| Arquitecto | Andrés Castro |
| Dev Senior | Isabella Moreno |
| QA Senior | Julián Ríos |
| Product Owner | Tomás Herrera |

---

*Documento Funcional v1.0 — Comité Experto de Turismo Digital*
