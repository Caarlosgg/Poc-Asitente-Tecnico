#!/usr/bin/env bash
# Limpia y reinicia la base de datos (DROP + recrear desde init.sql + seeds)
# ADVERTENCIA: Destruye todos los datos existentes

set -euo pipefail

DB_URL="${DATABASE_URL:-postgresql://poc_user:poc_password@localhost:5432/poc_asistente}"
DB_NAME="${POSTGRES_DB:-poc_asistente}"
DB_USER="${POSTGRES_USER:-poc_user}"

echo "==> ADVERTENCIA: Se eliminarán todos los datos de la BD '$DB_NAME'."
read -p "¿Continuar? (s/N): " confirm
if [[ "$confirm" != "s" && "$confirm" != "S" ]]; then
    echo "Cancelado."
    exit 0
fi

echo "==> Eliminando tablas existentes..."
psql "$DB_URL" -c "
DROP TABLE IF EXISTS embedding_jobs CASCADE;
DROP TABLE IF EXISTS knowledge_chunks CASCADE;
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS decision_logs CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS session_state CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS historical_cases CASCADE;
DROP TABLE IF EXISTS diagnostic_trees CASCADE;
DROP TABLE IF EXISTS faqs CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
"

echo "==> Reiniciando con migrations y seeds..."
bash "$(dirname "$0")/seed_db.sh"

echo "==> Reset completado."
