#!/bin/bash
set -e

echo "🔧 Installing dependencies..."
npm ci --legacy-peer-deps || npm install --legacy-peer-deps

echo "📦 Building React app..."
CI=false npm run build

echo "✅ Build completed successfully!"
