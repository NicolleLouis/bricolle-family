#!/usr/bin/env bash
set -euo pipefail

# This script reclaims disk space by cleaning Docker caches and common Python build artefacts
# without touching the database files or the postgres_data volume.

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${PROJECT_ROOT}"

log() {
    printf '[optimize_memory] %s\n' "$1"
}

log "Starting cleanup from ${PROJECT_ROOT}"

if command -v docker >/dev/null 2>&1; then
    log "Removing stopped containers (safe for the database volume)..."
    docker container prune -f >/dev/null

    log "Removing dangling images..."
    docker image prune -f >/dev/null

    log "Cleaning build cache..."
    docker builder prune -f >/dev/null

    log "Removing unused networks..."
    docker network prune -f >/dev/null

    log "Skipping docker volume pruning to preserve postgres_data and SQLite DB."
else
    log "Docker is not installed or not on PATH; skipping Docker cleanup."
fi

log "Removing Python bytecode caches..."
find "${PROJECT_ROOT}" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "${PROJECT_ROOT}" -name "*.py[cod]" -delete 2>/dev/null || true

log "Cleaning pytest caches..."
rm -rf "${PROJECT_ROOT}/.pytest_cache" 2>/dev/null || true

log "Cleanup complete."
