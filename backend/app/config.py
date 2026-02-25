from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Hacienda La Carmelita API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hacienda_carmelita"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/hacienda_carmelita"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production-use-doppler"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = "whatsapp:+14155238886"

    # SendGrid
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "reservas@haciendalacarmelita.com"
    SENDGRID_FROM_NAME: str = "Hacienda La Carmelita"

    # Wompi
    WOMPI_PUBLIC_KEY: str = ""
    WOMPI_PRIVATE_KEY: str = ""
    WOMPI_EVENTS_SECRET: str = ""
    WOMPI_INTEGRITY_KEY: str = ""
    WOMPI_SANDBOX: bool = True

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_SANDBOX: bool = True

    # URL base del frontend (para redirect URLs de pasarelas)
    FRONTEND_URL: str = "http://localhost:3000"

    # Anthropic / Claude API
    ANTHROPIC_API_KEY: str = ""

    # Channel Manager (Lodgify)
    LODGIFY_API_KEY: str = ""
    LODGIFY_BASE_URL: str = "https://api.lodgify.com/v2"
    LODGIFY_PROPERTY_ID: str = ""

    # Admin
    ADMIN_EMAIL: str = "admin@haciendalacarmelita.com"
    ADMIN_WHATSAPP: str = "+573000000000"

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://haciendalacarmelita.com",
        "https://www.haciendalacarmelita.com",
    ]

    # OTP
    OTP_LENGTH: int = 6
    OTP_TTL_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3
    OTP_RATE_LIMIT_PER_HOUR: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
