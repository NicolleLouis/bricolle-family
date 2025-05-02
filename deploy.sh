#!/bin/bash

echo "📦 Pulling latest changes from Git..."
git pull origin main

echo "🧹 Cleaning old containers..."
docker compose down -v

echo "🐳 Rebuilding containers..."
docker compose build

echo "🚀 Restarting app..."
docker compose up -d

echo "🐗 Running Migrations..."
docker compose exec web python manage.py migrate

echo "🦦 Collect Staticfiles..."
docker compose exec web python manage.py collectstatic --noinput

echo "✅ Done!"