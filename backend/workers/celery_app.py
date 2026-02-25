from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "hacienda_carmelita",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "workers.tasks",
        "workers.tasks.sincronizacion",
        "workers.tasks.agentes",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
    beat_schedule={
        # Sprint 8: Agente SEO — todos los lunes a las 7am (America/Bogota)
        "seo-semanal": {
            "task": "agentes.generar_articulo_seo",
            "schedule": crontab(hour=7, minute=0, day_of_week=1),
        },
        # Sprint 8: Agente GEO — cada 14 días (1209600 segundos)
        "geo-quincenal": {
            "task": "agentes.generar_contenido_geo",
            "schedule": 1209600.0,  # 14 días en segundos
        },
        # Sprint 4: Sincronización OTA — cada 15 minutos
        "sincronizar-ota-cada-15-min": {
            "task": "sincronizacion.sincronizar_ota",
            "schedule": 900.0,  # 15 minutos
        },
    },
)
