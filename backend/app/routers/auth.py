from __future__ import annotations

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session, select
from passlib.context import CryptContext
from app.database import get_sync_db
from app.models.usuario import Usuario
from app.auth.jwt import crear_access_token, crear_refresh_token, verificar_token
from app.auth.dependencies import get_current_user
from app.schemas.auth import RegistroRequest, LoginRequest, TokenResponse, UsuarioResponse, RefreshRequest
from app.schemas.otp import EnviarOTPRequest, VerificarOTPRequest, OTPResponse, OTPVerificadoResponse
from app.config import settings
import uuid
import hashlib

# SEC-001: contexto bcrypt para hashing y verificación de contraseñas
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)

router = APIRouter()


# ─────────────────────────────────────────────────────────────
#  REGISTRO
# ─────────────────────────────────────────────────────────────

@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registro(
    data: RegistroRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Registrar nuevo usuario.
    Si el email ya existe, retorna el usuario existente (sin error) para
    facilitar el flujo de reserva sin fricción.
    """
    # Verificar si ya existe
    existente = db.exec(
        select(Usuario).where(Usuario.email == data.email, Usuario.deleted_at == None)
    ).first()

    if existente:
        return UsuarioResponse(
            id=str(existente.id),
            email=existente.email,
            nombre=existente.nombre,
            apellido=existente.apellido,
            rol=existente.rol,
            email_verificado=existente.email_verificado,
            telefono_verificado=existente.telefono_verificado,
        )

    # Crear nuevo usuario
    nuevo = Usuario(
        email=data.email,
        nombre=data.nombre,
        apellido=data.apellido,
        telefono=data.telefono,
        pais=data.pais,
        idioma=data.idioma,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return UsuarioResponse(
        id=str(nuevo.id),
        email=nuevo.email,
        nombre=nuevo.nombre,
        apellido=nuevo.apellido,
        rol=nuevo.rol,
        email_verificado=nuevo.email_verificado,
        telefono_verificado=nuevo.telefono_verificado,
    )


# ─────────────────────────────────────────────────────────────
#  OTP — ENVIAR
# ─────────────────────────────────────────────────────────────

@router.post("/otp/enviar", response_model=OTPResponse)
async def enviar_otp(
    data: EnviarOTPRequest,
    request: Request,
    db: Session = Depends(get_sync_db),
):
    """
    Generar y enviar OTP por el canal elegido.
    Rate limit: 5 OTPs por destino por hora (via Redis cuando esté disponible).
    """
    from app.auth.otp import enviar_otp as _enviar_otp
    result = await _enviar_otp(
        destino=data.destino,
        canal=data.canal,
        proposito=data.proposito,
        usuario_id=data.usuario_id,
        db=db,
    )
    return OTPResponse(
        otp_id=result["otp_id"],
        canal=result["canal"],
        mensaje=f"Código enviado por {data.canal.upper()}",
        expires_en_minutos=10,
    )


# ─────────────────────────────────────────────────────────────
#  OTP — VERIFICAR
# ─────────────────────────────────────────────────────────────

@router.post("/otp/verificar", response_model=OTPVerificadoResponse)
async def verificar_otp_endpoint(
    data: VerificarOTPRequest,
    db: Session = Depends(get_sync_db),
):
    """
    Verificar código OTP. Si es correcto:
    - Marca el OTP como verificado
    - Retorna token temporal válido 30 minutos para completar la reserva/pago
    """
    from app.auth.otp import verificar_otp as _verificar_otp, obtener_otp_por_id
    from app.auth.jwt import crear_otp_token

    otp_record = obtener_otp_por_id(data.otp_id, db)
    if not otp_record:
        raise HTTPException(status_code=404, detail="OTP no encontrado")

    await _verificar_otp(data.otp_id, data.codigo, db)

    # Crear token temporal para el flujo de pago
    token = crear_otp_token(
        otp_id=data.otp_id,
        usuario_id=str(otp_record.usuario_id),
    )

    return OTPVerificadoResponse(
        verificado=True,
        mensaje="Identidad verificada correctamente",
        token=token,
    )


# ─────────────────────────────────────────────────────────────
#  LOGIN
# ─────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_sync_db),
):
    """
    Login para el panel de administración.
    - Acepta JSON body: { email, password }
    - Verifica contraseña con bcrypt (SEC-001)
    - Retorna JWT de acceso + sets refresh token en httpOnly cookie (SEC-002)
    """
    # 1. Buscar usuario admin/staff por email
    usuario = db.exec(
        select(Usuario).where(
            Usuario.email == data.email,
            Usuario.rol.in_(["admin", "staff"]),
            Usuario.deleted_at == None,  # noqa: E711
        )
    ).first()

    # Respuesta genérica para no revelar si el email existe (timing-safe)
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not usuario:
        raise credenciales_invalidas

    # 2. SEC-001: verificar contraseña con bcrypt
    if not usuario.password_hash:
        # Admin sin contraseña configurada — ejecutar seed_admin.py primero
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta sin contraseña. Ejecuta: python scripts/seed_admin.py",
        )

    if not verificar_password(data.password, usuario.password_hash):
        raise credenciales_invalidas

    # 3. Emitir tokens
    access_token = crear_access_token({"sub": str(usuario.id), "rol": usuario.rol})
    refresh_token = crear_refresh_token({"sub": str(usuario.id)})

    # Refresh token en httpOnly cookie (SEC-002 — solo el access va en el body)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=60 * 60 * 24 * 7,  # 7 días
    )

    return TokenResponse(
        access_token=access_token,
        usuario_id=str(usuario.id),
        rol=usuario.rol,
    )


# ─────────────────────────────────────────────────────────────
#  REFRESH
# ─────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: Session = Depends(get_sync_db),
):
    """Refrescar access token usando el refresh token de la cookie httpOnly."""
    refresh = request.cookies.get("refresh_token")
    if not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token no encontrado")

    payload = verificar_token(refresh, expected_type="refresh")
    user_id = payload.get("sub")

    usuario = db.exec(
        select(Usuario).where(Usuario.id == uuid.UUID(user_id), Usuario.deleted_at == None)
    ).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    new_access = crear_access_token({"sub": str(usuario.id), "rol": usuario.rol})
    return TokenResponse(
        access_token=new_access,
        usuario_id=str(usuario.id),
        rol=usuario.rol,
    )


# ─────────────────────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────────────────────

@router.delete("/logout")
async def logout(response: Response):
    """Invalidar sesión: eliminar cookie de refresh token."""
    response.delete_cookie("refresh_token")
    return {"message": "Sesión cerrada correctamente"}


# ─────────────────────────────────────────────────────────────
#  ME (perfil del usuario actual)
# ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UsuarioResponse)
async def get_me(current_user: Usuario = Depends(get_current_user)):
    """Obtener datos del usuario autenticado."""
    return UsuarioResponse(
        id=str(current_user.id),
        email=current_user.email,
        nombre=current_user.nombre,
        apellido=current_user.apellido,
        rol=current_user.rol,
        email_verificado=current_user.email_verificado,
        telefono_verificado=current_user.telefono_verificado,
    )
