from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers import auth, reservas, disponibilidad, pagos, admin, chat, agentes

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)


# Security headers middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' checkout.wompi.co js.stripe.com; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        "font-src 'self' fonts.gstatic.com; "
        "frame-src checkout.wompi.co js.stripe.com; "
        "img-src 'self' data: https:;"
    )
    return response


# Routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(reservas.router, prefix="/reservas", tags=["Reservas"])
app.include_router(disponibilidad.router, prefix="/disponibilidad", tags=["Disponibilidad"])
app.include_router(pagos.router, prefix="/pagos", tags=["Pagos"])
app.include_router(admin.router, prefix="/admin", tags=["Administración"])
app.include_router(chat.router, prefix="/chat", tags=["Chat IA"])
app.include_router(agentes.router, prefix="/agentes", tags=["Agentes IA"])


@app.get("/health", tags=["Sistema"])
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        },
    )


@app.get("/", tags=["Sistema"])
async def root():
    return {"message": "Hacienda La Carmelita API — v1.0.0"}
