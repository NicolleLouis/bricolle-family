#!/bin/bash

echo "📦 Pulling latest changes from Git..."
git pull origin main

echo "🐳 Rebuilding containers..."
docker compose build

echo "🚀 Restarting app..."
docker compose up -d

echo "✅ Done!"
