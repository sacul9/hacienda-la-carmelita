from __future__ import annotations
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.auth.jwt import verificar_token
from app.database import get_sync_db
from app.models.usuario import Usuario
import uuid

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_sync_db),
) -> Usuario:
    """Obtiene el usuario autenticado desde el JWT en el header Authorization."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verificar_token(credentials.credentials, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    usuario = db.exec(
        select(Usuario).where(Usuario.id == uuid.UUID(user_id), Usuario.deleted_at == None)
    ).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return usuario


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_sync_db),
) -> Usuario | None:
    """Igual que get_current_user pero retorna None si no hay token (para rutas públicas opcionales)."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def require_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica que el usuario tiene rol admin."""
    if current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol admin")
    return current_user


async def require_staff(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica que el usuario tiene rol staff o admin."""
    if current_user.rol not in ("admin", "staff"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol staff o admin")
    return current_user


def get_otp_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Valida el token temporal de OTP verificado.
    Se usa en los endpoints de creación de reserva y pago.
    """
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token OTP requerido")
    return verificar_token(credentials.credentials, expected_type="otp_verified")
