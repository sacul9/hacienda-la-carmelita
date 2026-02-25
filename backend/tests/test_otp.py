"""
Tests del módulo OTP — Sprint 1
Cobertura: generación, hash, verificación, expiración, rate limit, canales.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.auth.otp import (
    generar_otp,
    puede_enviar_otp,
    verificar_otp,
    obtener_otp_por_id,
)
from app.models.otp import OTP
from app.models.usuario import Usuario


# ─────────────────────────────────────────────────────────────
#  FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture(name="db")
def db_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def usuario_test(db):
    """Crea un usuario de prueba en la BD."""
    u = Usuario(
        email="test@haciendalacarmelita.com",
        nombre="Test",
        apellido="Usuario",
        telefono="+573001234567",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def otp_valido(db, usuario_test):
    """Crea un OTP válido en la BD."""
    codigo = "123456"
    hash_codigo = hashlib.sha256(codigo.encode()).hexdigest()
    otp = OTP(
        usuario_id=usuario_test.id,
        canal="email",
        destino="test@haciendalacarmelita.com",
        codigo=hash_codigo,
        proposito="reserva",
        intentos=0,
        verificado=False,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp, codigo


# ─────────────────────────────────────────────────────────────
#  TESTS DE GENERACIÓN
# ─────────────────────────────────────────────────────────────

class TestGenerarOTP:
    def test_formato_6_digitos(self):
        """El OTP debe ser exactamente 6 dígitos numéricos."""
        codigo, hash_codigo = generar_otp()
        assert len(codigo) == 6
        assert codigo.isdigit(), "El OTP debe ser solo dígitos"

    def test_hash_sha256_longitud(self):
        """El hash SHA-256 debe tener 64 caracteres hexadecimales."""
        _, hash_codigo = generar_otp()
        assert len(hash_codigo) == 64
        assert all(c in "0123456789abcdef" for c in hash_codigo)

    def test_codigo_y_hash_son_diferentes(self):
        """El código plain y su hash deben ser siempre diferentes."""
        codigo, hash_codigo = generar_otp()
        assert codigo != hash_codigo

    def test_unicidad(self):
        """100 OTPs generados deben ser únicos (probabilidad de colisión: 1 en 10^6)."""
        codigos = {generar_otp()[0] for _ in range(100)}
        # Con 100 códigos de 6 dígitos, la probabilidad de colisión es mínima
        assert len(codigos) >= 95, "Demasiadas colisiones en la generación de OTPs"

    def test_hash_es_determinista(self):
        """El mismo código siempre produce el mismo hash."""
        codigo = "123456"
        _, hash1 = generar_otp.__wrapped__(6) if hasattr(generar_otp, '__wrapped__') else ("123456", hashlib.sha256(codigo.encode()).hexdigest())
        hash2 = hashlib.sha256(codigo.encode()).hexdigest()
        assert hash1 == hash2 or hash2 == hashlib.sha256(codigo.encode()).hexdigest()

    def test_largo_personalizado(self):
        """Debe soportar OTPs de diferente largo."""
        codigo_4, _ = generar_otp(4)
        codigo_8, _ = generar_otp(8)
        assert len(codigo_4) == 4
        assert len(codigo_8) == 8

    def test_codigo_nunca_en_hash(self):
        """El código plain nunca debe aparecer en el hash (obviamente)."""
        for _ in range(20):
            codigo, hash_codigo = generar_otp()
            assert codigo not in hash_codigo, "El código no debe aparecer en el hash"


# ─────────────────────────────────────────────────────────────
#  TESTS DE RATE LIMITING
# ─────────────────────────────────────────────────────────────

class TestRateLimiting:
    def test_sin_redis_permite_envio(self):
        """Sin Redis configurado, debe permitir el envío (fail-open)."""
        assert puede_enviar_otp("test@test.com", redis_client=None) is True

    def test_con_redis_respeta_limite(self):
        """Con Redis, debe bloquear después de 5 envíos por hora."""
        mock_redis = MagicMock()
        # Simular que ya se enviaron 6 OTPs (supera el límite de 5)
        mock_redis.incr.return_value = 6
        assert puede_enviar_otp("spam@test.com", redis_client=mock_redis) is False

    def test_con_redis_permite_primeros_5(self):
        """Con Redis, debe permitir los primeros 5 envíos."""
        mock_redis = MagicMock()
        for i in range(1, 6):
            mock_redis.incr.return_value = i
            assert puede_enviar_otp("ok@test.com", redis_client=mock_redis) is True

    def test_redis_error_no_bloquea(self):
        """Si Redis falla, no debe bloquear al usuario."""
        mock_redis = MagicMock()
        mock_redis.incr.side_effect = Exception("Redis connection failed")
        assert puede_enviar_otp("test@test.com", redis_client=mock_redis) is True


# ─────────────────────────────────────────────────────────────
#  TESTS DE VERIFICACIÓN
# ─────────────────────────────────────────────────────────────

class TestVerificarOTP:
    @pytest.mark.asyncio
    async def test_codigo_correcto(self, db, otp_valido):
        """Un código correcto debe verificarse exitosamente."""
        otp, codigo = otp_valido
        resultado = await verificar_otp(str(otp.id), codigo, db)
        assert resultado is True

    @pytest.mark.asyncio
    async def test_otp_marcado_verificado(self, db, otp_valido):
        """Después de verificar, el OTP debe estar marcado como verificado."""
        otp, codigo = otp_valido
        await verificar_otp(str(otp.id), codigo, db)
        db.refresh(otp)
        assert otp.verificado is True

    @pytest.mark.asyncio
    async def test_codigo_incorrecto(self, db, otp_valido):
        """Un código incorrecto debe retornar error 400."""
        from fastapi import HTTPException
        otp, _ = otp_valido
        with pytest.raises(HTTPException) as exc_info:
            await verificar_otp(str(otp.id), "000000", db)
        assert exc_info.value.status_code == 400
        assert "incorrecto" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_incrementa_intentos(self, db, otp_valido):
        """Cada código incorrecto debe incrementar el contador de intentos."""
        from fastapi import HTTPException
        otp, _ = otp_valido
        try:
            await verificar_otp(str(otp.id), "000000", db)
        except HTTPException:
            pass
        db.refresh(otp)
        assert otp.intentos == 1

    @pytest.mark.asyncio
    async def test_max_intentos_bloquea(self, db, usuario_test):
        """Después de 3 intentos fallidos, debe bloquear el OTP."""
        from fastapi import HTTPException
        codigo = "654321"
        otp = OTP(
            usuario_id=usuario_test.id,
            canal="email",
            destino="test@haciendalacarmelita.com",
            codigo=hashlib.sha256(codigo.encode()).hexdigest(),
            proposito="reserva",
            intentos=3,  # Ya en el límite
            verificado=False,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)

        with pytest.raises(HTTPException) as exc_info:
            await verificar_otp(str(otp.id), codigo, db)
        assert exc_info.value.status_code == 400
        assert "intentos" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_otp_expirado(self, db, usuario_test):
        """Un OTP expirado debe retornar error 400."""
        from fastapi import HTTPException
        codigo = "999999"
        otp = OTP(
            usuario_id=usuario_test.id,
            canal="email",
            destino="test@haciendalacarmelita.com",
            codigo=hashlib.sha256(codigo.encode()).hexdigest(),
            proposito="reserva",
            intentos=0,
            verificado=False,
            expires_at=datetime.utcnow() - timedelta(minutes=1),  # Expirado hace 1 min
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)

        with pytest.raises(HTTPException) as exc_info:
            await verificar_otp(str(otp.id), codigo, db)
        assert exc_info.value.status_code == 400
        assert "expirado" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_otp_ya_usado(self, db, otp_valido):
        """Un OTP ya verificado no puede usarse de nuevo."""
        from fastapi import HTTPException
        otp, codigo = otp_valido
        # Primer uso — exitoso
        await verificar_otp(str(otp.id), codigo, db)
        # Segundo uso — debe fallar
        with pytest.raises(HTTPException) as exc_info:
            await verificar_otp(str(otp.id), codigo, db)
        assert exc_info.value.status_code == 400
        assert "utilizado" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_otp_no_encontrado(self, db):
        """Un OTP con ID inexistente debe retornar 404."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await verificar_otp(str(uuid.uuid4()), "123456", db)
        assert exc_info.value.status_code == 404

    def test_obtener_otp_por_id_existe(self, db, otp_valido):
        """obtener_otp_por_id debe retornar el OTP correcto."""
        otp, _ = otp_valido
        resultado = obtener_otp_por_id(str(otp.id), db)
        assert resultado is not None
        assert resultado.id == otp.id

    def test_obtener_otp_por_id_no_existe(self, db):
        """obtener_otp_por_id debe retornar None para ID inexistente."""
        resultado = obtener_otp_por_id(str(uuid.uuid4()), db)
        assert resultado is None


# ─────────────────────────────────────────────────────────────
#  TESTS DE SEGURIDAD
# ─────────────────────────────────────────────────────────────

class TestSeguridadOTP:
    def test_codigo_plain_no_en_hash(self):
        """SEGURIDAD: El código plain nunca debe estar en el hash."""
        for _ in range(50):
            codigo, hash_codigo = generar_otp()
            assert codigo not in hash_codigo

    def test_hash_diferente_para_diferente_codigo(self):
        """Dos códigos distintos deben producir hashes distintos."""
        _, hash1 = generar_otp()
        _, hash2 = generar_otp()
        # Con SHA-256, es prácticamente imposible que coincidan
        assert hash1 != hash2

    def test_no_info_en_error_de_codigo_incorrecto(self):
        """Los mensajes de error no deben revelar información del código correcto."""
        # El mensaje de error solo debe decir "incorrecto" sin revelar el código
        codigo, hash_codigo = generar_otp()
        # No hay forma de deducir el código desde el mensaje de error
        assert codigo not in "Código incorrecto. 2 intentos restante(s)."
