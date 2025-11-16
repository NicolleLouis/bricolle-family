#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "${PROJECT_ROOT}"

echo "🔐 Preparing TLS folders..."
./scripts/manage_certs.sh bootstrap

echo "📦 Pulling latest changes from Git..."
git pull origin main

echo "🐳 Rebuilding containers..."
docker compose build

echo "🚀 Restarting app..."
docker compose up -d

echo "🐗 Running Migrations..."
docker compose exec web python manage.py migrate

echo "🦦 Collect Staticfiles..."
docker compose exec web python manage.py collectstatic --noinput

echo "♻️  Refreshing TLS certificates..."
./scripts/manage_certs.sh renew

echo "✅ Done!"
