#!/usr/bin/env bash

set -euo pipefail

# Installs Docker Desktop on macOS (via Homebrew), waits for Docker Engine,
# generates PgBouncer config, and deploys PgBouncer with docker compose.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PGB_DIR="$ROOT_DIR/infra/pgbouncer"
COMPOSE_FILE="$ROOT_DIR/infra/pgbouncer/docker-compose.pgbouncer.yml"

DB_HOST="${DB_HOST:-host.docker.internal}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-ats_platform}"
DB_USER="${DB_USER:-ats_user}"
DB_PASSWORD="${DB_PASSWORD:-ats_password}"

PGBOUNCER_PORT="${PGBOUNCER_PORT:-6432}"
POOL_MODE="${POOL_MODE:-transaction}"
MAX_CLIENT_CONN="${MAX_CLIENT_CONN:-200}"
DEFAULT_POOL_SIZE="${DEFAULT_POOL_SIZE:-25}"
MIN_POOL_SIZE="${MIN_POOL_SIZE:-5}"
RESERVE_POOL_SIZE="${RESERVE_POOL_SIZE:-5}"
RESERVE_POOL_TIMEOUT="${RESERVE_POOL_TIMEOUT:-5}"
SERVER_RESET_QUERY="${SERVER_RESET_QUERY:-DISCARD ALL}"
ADMIN_USERS="${ADMIN_USERS:-$DB_USER}"
STATS_USERS="${STATS_USERS:-$DB_USER}"

echo "==> Checking Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "==> Installing Docker Desktop (if needed)"
if ! brew list --cask docker >/dev/null 2>&1; then
  brew install --cask docker
fi

echo "==> Starting Docker Desktop"
open -a Docker || true

echo "==> Waiting for Docker Engine to become ready"
for i in {1..60}; do
  if docker info >/dev/null 2>&1; then
    break
  fi
  sleep 2
  if [ "$i" -eq 60 ]; then
    echo "Docker did not become ready in time."
    exit 1
  fi
done

echo "==> Verifying docker compose"
docker compose version >/dev/null

echo "==> Generating PgBouncer config in $PGB_DIR"
mkdir -p "$PGB_DIR"

MD5_PASS="$(printf "%s" "${DB_PASSWORD}${DB_USER}" | md5 -q)"

cat > "$PGB_DIR/pgbouncer.ini" <<EOF
[databases]
${DB_NAME} = host=${DB_HOST} port=${DB_PORT} dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD}

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 5432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = ${POOL_MODE}
max_client_conn = ${MAX_CLIENT_CONN}
default_pool_size = ${DEFAULT_POOL_SIZE}
min_pool_size = ${MIN_POOL_SIZE}
reserve_pool_size = ${RESERVE_POOL_SIZE}
reserve_pool_timeout = ${RESERVE_POOL_TIMEOUT}
server_reset_query = ${SERVER_RESET_QUERY}
ignore_startup_parameters = extra_float_digits,options
admin_users = ${ADMIN_USERS}
stats_users = ${STATS_USERS}
EOF

cat > "$PGB_DIR/userlist.txt" <<EOF
"${DB_USER}" "md5${MD5_PASS}"
EOF

echo "==> Deploying PgBouncer"
(
  cd "$PGB_DIR"
  docker compose -f docker-compose.pgbouncer.yml up -d
)

echo
echo "PgBouncer is running on localhost:${PGBOUNCER_PORT}"
echo "Use this connection string from apps:"
echo "postgresql://${DB_USER}:${DB_PASSWORD}@localhost:${PGBOUNCER_PORT}/${DB_NAME}"
echo
echo "Useful commands:"
echo "  cd \"$PGB_DIR\" && docker compose -f docker-compose.pgbouncer.yml ps"
echo "  cd \"$PGB_DIR\" && docker compose -f docker-compose.pgbouncer.yml logs -f pgbouncer"
