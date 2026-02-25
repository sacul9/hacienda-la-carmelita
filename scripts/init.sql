-- Script de inicialización de la base de datos
-- Este script corre automáticamente al levantar el contenedor de PostgreSQL por primera vez

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Comentario: Los modelos SQLModel crean las tablas automáticamente.
-- Este script solo instala las extensiones de PostgreSQL necesarias.

-- Índices adicionales de performance (se crean después de que SQLModel cree las tablas)
-- Los índices de las tablas se definen en los modelos SQLModel directamente.

SELECT 'Base de datos Hacienda La Carmelita inicializada correctamente.' AS mensaje;
