from __future__ import annotations
from pydantic import BaseModel
from typing import Literal, Optional


class EnviarOTPRequest(BaseModel):
    destino: str          # email o teléfono
    canal: Literal["email", "sms", "whatsapp"]
    proposito: Literal["registro", "reserva", "login", "pago"]
    usuario_id: str


class VerificarOTPRequest(BaseModel):
    otp_id: str
    codigo: str           # 6 dígitos en texto


class OTPResponse(BaseModel):
    otp_id: str
    canal: str
    mensaje: str
    expires_en_minutos: int = 10


class OTPVerificadoResponse(BaseModel):
    verificado: bool
    mensaje: str
    token: Optional[str] = None   # token temporal para reserva/pago
