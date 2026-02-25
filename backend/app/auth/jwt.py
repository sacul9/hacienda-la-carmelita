from datetime import datetime, timedelta
from typing import Optional
import uuid
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings


def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea JWT de acceso con TTL de 15 minutos."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def crear_refresh_token(data: dict) -> str:
    """Crea JWT de refresh con TTL de 7 días."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def crear_otp_token(otp_id: str, usuario_id: str) -> str:
    """
    Crea token temporal válido 30 minutos, usado SOLO para iniciar el pago
    después de que el OTP fue verificado exitosamente.
    """
    data = {
        "sub": usuario_id,
        "otp_id": otp_id,
        "type": "otp_verified",
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verificar_token(token: str, expected_type: str = "access") -> dict:
    """
    Verifica y decodifica un JWT.
    Retorna el payload si es válido, lanza HTTPException si no.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception
