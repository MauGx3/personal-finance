#!/bin/bash
# Local documentation build script

set -e

echo "Building Personal Finance Documentation..."

# Change to docs directory
cd "$(dirname "$0")/docs"

# Set environment variables for Django
export DATABASE_URL="sqlite:///docs_build.db"
export DJANGO_SETTINGS_MODULE="config.settings.local"
export DJANGO_SECRET_KEY="local-docs-build-key"

# Clean previous builds
echo "Cleaning previous builds..."
make clean

# Build HTML documentation
echo "Building HTML documentation..."
make html

echo "✅ Documentation built successfully!"
echo "📖 Open docs/_build/html/index.html in your browser to view the documentation"

# Optional: Start development server
read -p "Start local docs server? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting documentation server at http://localhost:8000"
    echo "   Press Ctrl+C to stop"
    cd _build/html
    python -m http.server 8000
fi
