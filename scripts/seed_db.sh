#!/usr/bin/env bash
# Ejecuta los seeds de la base de datos en orden correcto respetando FK constraints

set -euo pipefail

DB_URL="${DATABASE_URL:-postgresql://poc_user:poc_password@localhost:5432/poc_asistente}"

echo "==> Ejecutando seeds en orden..."

echo "  [1/5] Migraciones..."
psql "$DB_URL" -f "$(dirname "$0")/../backend/db/migrations/init.sql"

echo "  [2/5] Vehículos..."
psql "$DB_URL" -f "$(dirname "$0")/../backend/db/seeds/vehicles.sql"

echo "  [3/5] FAQs..."
psql "$DB_URL" -f "$(dirname "$0")/../backend/db/seeds/faqs.sql"

echo "  [4/5] Árboles de diagnóstico..."
psql "$DB_URL" -f "$(dirname "$0")/../backend/db/seeds/diagnostic_trees.sql"

echo "  [5/5] Casos históricos..."
psql "$DB_URL" -f "$(dirname "$0")/../backend/db/seeds/historical_cases.sql"

echo "==> Seeds completados."
