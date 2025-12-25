#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DATE=$(date +"%Y-%m-%d_%H-%M")
BACKUP_DIR="$SCRIPT_DIR/backups"
FILENAME="$BACKUP_DIR/pg_dump_$DATE.sql"

mkdir -p "$BACKUP_DIR"

docker compose -f "$SCRIPT_DIR/docker-compose.yml" exec -T db pg_dump -U postgres -d postgres > "$FILENAME"

find "$BACKUP_DIR" -type f -name "*.sql" -mtime +7 -delete
