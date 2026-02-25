from pydantic import BaseModel, EmailStr, field_validator
import re


class RegistroRequest(BaseModel):
    email: EmailStr
    nombre: str
    apellido: str
    telefono: str
    pais: str = "CO"
    idioma: str = "es"

    @field_validator("nombre", "apellido")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("No puede estar vacío")
        return v.strip()

    @field_validator("telefono")
    @classmethod
    def telefono_valido(cls, v: str) -> str:
        limpio = re.sub(r"[\s\-\(\)]", "", v)
        if not limpio.startswith("+"):
            limpio = "+" + limpio
        if len(limpio) < 10:
            raise ValueError("Teléfono inválido")
        return limpio


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario_id: str
    rol: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UsuarioResponse(BaseModel):
    id: str
    email: str
    nombre: str
    apellido: str
    rol: str
    email_verificado: bool
    telefono_verificado: bool
