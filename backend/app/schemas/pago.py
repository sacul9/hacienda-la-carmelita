from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class IniciarPagoWompiRequest(BaseModel):
    reserva_id: str
    moneda: str = "COP"


class WompiTransaccionResponse(BaseModel):
    acceptance_token: str
    monto_en_centavos: int
    moneda: str
    referencia: str
    public_key: str


class IniciarPagoStripeRequest(BaseModel):
    reserva_id: str
    moneda: str = "usd"


class StripeIntentResponse(BaseModel):
    client_secret: str
    monto: int
    moneda: str
    publishable_key: str


class PagoEstadoResponse(BaseModel):
    pago_id: str
    estado: str
    monto: Decimal
    moneda: str
    pasarela: str
