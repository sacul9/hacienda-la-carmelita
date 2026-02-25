"""
Módulo OTP — Verificación de identidad en 3 canales.

Reglas de seguridad (NO NEGOCIABLES):
- El código OTP plain NUNCA se almacena en BD
- Solo el hash SHA-256 se guarda
- TTL: 10 minutos
- Máx 3 intentos por OTP
- Rate limit: 5 OTPs por destino por hora
- Al fallar 3 veces: OTP invalidado, debe solicitar nuevo
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select, update

from app.config import settings
from app.models.otp import OTP


# ─────────────────────────────────────────────────────────────
#  GENERACIÓN
# ─────────────────────────────────────────────────────────────

def generar_otp(largo: int = 6) -> tuple[str, str]:
    """
    Genera OTP de N dígitos usando secrets (criptográficamente seguro).
    Retorna (codigo_plain, codigo_hash_sha256).
    El codigo_plain SOLO se envía al usuario y NUNCA se persiste.
    """
    codigo = "".join([str(secrets.randbelow(10)) for _ in range(largo)])
    hash_codigo = hashlib.sha256(codigo.encode()).hexdigest()
    return codigo, hash_codigo


# ─────────────────────────────────────────────────────────────
#  RATE LIMITING
# ─────────────────────────────────────────────────────────────

def puede_enviar_otp(destino: str, redis_client=None) -> bool:
    """
    Rate limiting: máx 5 OTPs por destino por hora.
    Si Redis no está disponible, permite el envío (fail-open para no bloquear a usuarios).
    """
    if redis_client is None:
        # Redis no configurado en este entorno — permitir (TODO: conectar Redis en staging)
        return True
    try:
        key = f"otp_rate:{destino}"
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, 3600)  # 1 hora
        return count <= settings.OTP_RATE_LIMIT_PER_HOUR
    except Exception:
        return True  # fail-open si Redis no responde


# ─────────────────────────────────────────────────────────────
#  ENVÍO
# ─────────────────────────────────────────────────────────────

async def enviar_otp(
    destino: str,
    canal: str,
    proposito: str,
    usuario_id: str,
    db: Session,
    redis_client=None,
) -> dict:
    """
    Flujo completo:
    1. Verificar rate limit
    2. Invalidar OTPs anteriores del mismo destino/propósito
    3. Generar nuevo OTP
    4. Guardar hash en BD
    5. Enviar por canal elegido
    """
    # 1. Rate limit
    if not puede_enviar_otp(destino, redis_client):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera 1 hora antes de solicitar otro código.",
        )

    # 2. Invalidar OTPs anteriores pendientes del mismo destino/propósito
    otps_anteriores = db.exec(
        select(OTP).where(
            OTP.destino == destino,
            OTP.proposito == proposito,
            OTP.verificado == False,
        )
    ).all()
    for otp in otps_anteriores:
        otp.verificado = True  # invalidar marcando como "usado"
    if otps_anteriores:
        db.commit()

    # 3. Generar OTP
    codigo_plain, codigo_hash = generar_otp(settings.OTP_LENGTH)
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_TTL_MINUTES)

    # 4. Guardar en BD (solo el hash)
    otp_record = OTP(
        usuario_id=uuid.UUID(usuario_id) if usuario_id else None,
        canal=canal,
        destino=destino,
        codigo=codigo_hash,      # NUNCA el código plain
        proposito=proposito,
        intentos=0,
        verificado=False,
        expires_at=expires_at,
    )
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    # 5. Enviar por el canal
    mensaje = (
        f"Tu código de verificación para Hacienda La Carmelita es: {codigo_plain}. "
        f"Válido por {settings.OTP_TTL_MINUTES} minutos. No lo compartas."
    )

    try:
        if canal == "email":
            from app.notificaciones.email import send_otp_email
            await send_otp_email(destino=destino, codigo=codigo_plain)
        elif canal == "sms":
            from app.notificaciones.whatsapp import send_sms_otp
            await send_sms_otp(telefono=destino, mensaje=mensaje)
        elif canal == "whatsapp":
            from app.notificaciones.whatsapp import send_whatsapp_otp
            await send_whatsapp_otp(telefono=destino, codigo=codigo_plain)
        else:
            raise HTTPException(status_code=400, detail=f"Canal no válido: {canal}")
    except HTTPException:
        raise
    except Exception as e:
        # No fallar la petición si el envío falla — el OTP está en BD
        # El usuario puede pedir reenvío
        print(f"[OTP] Error enviando por {canal}: {e}")

    return {
        "otp_id": str(otp_record.id),
        "canal": canal,
        "expires_at": expires_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────
#  VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

async def verificar_otp(otp_id: str, codigo_ingresado: str, db: Session) -> bool:
    """
    Verifica el código OTP ingresado.
    - Máx 3 intentos
    - TTL 10 minutos
    - Comparación de hash SHA-256 (timing-safe)
    """
    otp = db.exec(select(OTP).where(OTP.id == uuid.UUID(otp_id))).first()

    if not otp:
        raise HTTPException(status_code=404, detail="OTP no encontrado")

    if otp.verificado:
        raise HTTPException(status_code=400, detail="Este código ya fue utilizado")

    if datetime.utcnow() > otp.expires_at:
        raise HTTPException(
            status_code=400,
            detail="El código ha expirado. Solicita uno nuevo.",
        )

    if otp.intentos >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=400,
            detail="Demasiados intentos fallidos. Solicita un nuevo código.",
        )

    # Verificar hash con comparación de tiempo constante (evita timing attacks)
    hash_ingresado = hashlib.sha256(codigo_ingresado.encode()).hexdigest()

    # secrets.compare_digest previene timing attacks
    if not secrets.compare_digest(hash_ingresado, otp.codigo):
        otp.intentos += 1
        db.commit()
        intentos_restantes = settings.OTP_MAX_ATTEMPTS - otp.intentos
        if intentos_restantes <= 0:
            raise HTTPException(
                status_code=400,
                detail="Demasiados intentos fallidos. Solicita un nuevo código.",
            )
        raise HTTPException(
            status_code=400,
            detail=f"Código incorrecto. {intentos_restantes} {'intento' if intentos_restantes == 1 else 'intentos'} restante(s).",
        )

    # Código correcto — marcar como verificado
    otp.verificado = True
    db.commit()

    # Actualizar el campo verificado en el usuario según el canal
    _marcar_canal_verificado(otp, db)

    return True


def _marcar_canal_verificado(otp: OTP, db: Session) -> None:
    """Marca el canal (email o teléfono) como verificado en el usuario."""
    if not otp.usuario_id:
        return
    from app.models.usuario import Usuario
    usuario = db.exec(select(Usuario).where(Usuario.id == otp.usuario_id)).first()
    if not usuario:
        return
    if otp.canal == "email":
        usuario.email_verificado = True
    elif otp.canal in ("sms", "whatsapp"):
        usuario.telefono_verificado = True
    db.commit()


def obtener_otp_por_id(otp_id: str, db: Session) -> Optional[OTP]:
    """Helper para obtener un OTP por su ID."""
    try:
        return db.exec(select(OTP).where(OTP.id == uuid.UUID(otp_id))).first()
    except Exception:
        return None
