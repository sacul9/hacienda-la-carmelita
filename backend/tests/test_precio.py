"""Tests unitarios del servicio de precio — Sprint 2.

Sin BD ni HTTP: prueba directamente las funciones puras de precio.py.
"""
from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from app.services.precio import (
    calcular_precio,
    es_temporada_alta,
    TARIFA_BAJA,
    TARIFA_ALTA,
    TASA_USD,
)

# ─── Fechas de referencia ─────────────────────────────────────────────────────
# date(2025, 8, 1) = Viernes  (weekday=4) → temporada alta
# date(2025, 8, 4) = Lunes    (weekday=0) → temporada baja
VIERNES = date(2025, 8, 1)
SABADO  = date(2025, 8, 2)
DOMINGO = date(2025, 8, 3)
LUNES   = date(2025, 8, 4)
MARTES  = date(2025, 8, 5)
MIERCOLES = date(2025, 8, 6)
JUEVES  = date(2025, 8, 7)


class TestTemporadaAlta:
    def test_viernes_es_alta(self):
        """Viernes (weekday=4) debe ser temporada alta."""
        assert es_temporada_alta(VIERNES) is True

    def test_sabado_es_alta(self):
        """Sábado (weekday=5) debe ser temporada alta."""
        assert es_temporada_alta(SABADO) is True

    def test_domingo_es_alta(self):
        """Domingo (weekday=6) debe ser temporada alta."""
        assert es_temporada_alta(DOMINGO) is True

    def test_lunes_es_baja(self):
        """Lunes (weekday=0) debe ser temporada baja."""
        assert es_temporada_alta(LUNES) is False

    def test_martes_es_baja(self):
        """Martes (weekday=1) debe ser temporada baja."""
        assert es_temporada_alta(MARTES) is False

    def test_miercoles_es_baja(self):
        """Miércoles (weekday=2) debe ser temporada baja."""
        assert es_temporada_alta(MIERCOLES) is False

    def test_jueves_es_baja(self):
        """Jueves (weekday=3) debe ser temporada baja."""
        assert es_temporada_alta(JUEVES) is False


class TestCalcularPrecio:
    def test_2_noches_lunes_martes(self):
        """2 noches de lunes a miércoles → total = TARIFA_BAJA * 2."""
        # checkin=Lunes, checkout=Miércoles → noches: Lun + Mar
        resultado = calcular_precio(LUNES, MIERCOLES)
        assert resultado["total_cop"] == TARIFA_BAJA * 2

    def test_2_noches_viernes_sabado(self):
        """2 noches de viernes a domingo → total = TARIFA_ALTA * 2."""
        # checkin=Viernes, checkout=Domingo → noches: Vie + Sáb
        resultado = calcular_precio(VIERNES, DOMINGO)
        assert resultado["total_cop"] == TARIFA_ALTA * 2

    def test_semana_mixta_5_noches(self):
        """5 noches lun→sáb → 4 noches baja + 1 noche alta."""
        # Lun(baja), Mar(baja), Mie(baja), Jue(baja), Vie(alta) = 4*BAJA + 1*ALTA
        checkin  = LUNES
        checkout = date(2025, 8, 9)  # Sábado → 5 noches
        resultado = calcular_precio(checkin, checkout)
        esperado = TARIFA_BAJA * 4 + TARIFA_ALTA * 1
        assert resultado["total_cop"] == esperado

    def test_noches_calculadas_correctamente(self):
        """El campo 'noches' debe ser igual a (checkout - checkin).days."""
        checkin  = LUNES
        checkout = date(2025, 8, 8)  # Viernes → 4 noches
        resultado = calcular_precio(checkin, checkout)
        assert resultado["noches"] == (checkout - checkin).days

    def test_desglose_tiene_una_entrada_por_noche(self):
        """len(desglose) debe coincidir con el número de noches."""
        checkin  = LUNES
        checkout = date(2025, 8, 8)  # 4 noches
        resultado = calcular_precio(checkin, checkout)
        assert len(resultado["desglose"]) == resultado["noches"]

    def test_total_usd_aproximado(self):
        """total_usd == total_cop / TASA_USD con 2 decimales."""
        resultado = calcular_precio(LUNES, MIERCOLES)
        esperado = (resultado["total_cop"] / TASA_USD).quantize(Decimal("0.01"))
        assert resultado["total_usd"] == esperado

    def test_addons_cop_es_cero_para_mvp(self):
        """addons_cop siempre es 0 en MVP (Sprint 3 los integrará)."""
        resultado = calcular_precio(LUNES, MIERCOLES)
        assert resultado["addons_cop"] == Decimal("0")

    def test_menos_de_2_noches_lanza_error(self):
        """Solicitar 1 noche debe lanzar ValueError."""
        with pytest.raises(ValueError, match="2 noches"):
            calcular_precio(LUNES, MARTES)

    def test_exactamente_2_noches_no_lanza_error(self):
        """El mínimo permitido (2 noches) no debe lanzar error."""
        resultado = calcular_precio(LUNES, MIERCOLES)
        assert resultado["noches"] == 2

    def test_desglose_contiene_concepto_y_monto(self):
        """Cada entrada del desglose debe tener llaves 'concepto' y 'monto'."""
        resultado = calcular_precio(VIERNES, DOMINGO)
        for entrada in resultado["desglose"]:
            assert "concepto" in entrada
            assert "monto" in entrada

    def test_precio_base_cop_igual_total_sin_addons(self):
        """precio_base_cop + addons_cop debe igualar total_cop."""
        resultado = calcular_precio(LUNES, MIERCOLES)
        assert resultado["precio_base_cop"] + resultado["addons_cop"] == resultado["total_cop"]
