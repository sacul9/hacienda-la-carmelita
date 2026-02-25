#!/usr/bin/env python3
"""
Crea el usuario admin inicial para el entorno de desarrollo.
Uso: cd backend && python scripts/seed_admin.py

Credenciales por defecto:
  Email:    admin@haciendalacarmelita.com
  Password: admin123
"""
from __future__ import annotations

import sys
import os

# Asegurar que el módulo app sea importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from sqlmodel import Session, select, SQLModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_EMAIL = "admin@haciendalacarmelita.com"
ADMIN_PASSWORD = "admin123"  # Cambia en producción
ADMIN_NOMBRE = "Admin"
ADMIN_APELLIDO = "Carmelita"
ADMIN_TELEFONO = "+573001234567"


def main():
    # Importar después de configurar el path
    from app.database import _get_sync_engine
    from app.models.usuario import Usuario

    engine = _get_sync_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as db:
        existente = db.exec(
            select(Usuario).where(Usuario.email == ADMIN_EMAIL)
        ).first()

        if existente:
            print(f"Admin ya existe: {existente.email} (rol: {existente.rol})")
            if not existente.password_hash:
                existente.password_hash = pwd_context.hash(ADMIN_PASSWORD)
                db.add(existente)
                db.commit()
                print(f"Password actualizado a: {ADMIN_PASSWORD}")
            return

        admin = Usuario(
            email=ADMIN_EMAIL,
            nombre=ADMIN_NOMBRE,
            apellido=ADMIN_APELLIDO,
            telefono=ADMIN_TELEFONO,
            rol="admin",
            password_hash=pwd_context.hash(ADMIN_PASSWORD),
            email_verificado=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("Usuario admin creado exitosamente")
        print(f"   Email:    {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print(f"   ID:       {admin.id}")
        print()
        print("AVISO: Cambia la contrasena en produccion.")


if __name__ == "__main__":
    main()
