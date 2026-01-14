#!/bin/bash
# Script para desplegar el frontend a GitHub Pages

set -e  # Salir si hay algún error

echo "🚀 Desplegando frontend a GitHub Pages..."
echo ""

# Verificar que estamos en la rama main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  No estás en la rama main. Cambiando a main..."
    git checkout main
fi

# Guardar cualquier cambio pendiente
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Hay cambios sin commitear. Por favor, hace commit primero."
    exit 1
fi

echo "✓ Verificaciones completadas"
echo ""

# Crear/actualizar rama gh-pages
echo "📦 Preparando rama gh-pages..."

# Verificar si existe la rama gh-pages
if git show-ref --verify --quiet refs/heads/gh-pages; then
    echo "✓ Rama gh-pages ya existe, actualizando..."
    git checkout gh-pages
    git rm -rf .
    git checkout main -- frontend/*
else
    echo "✓ Creando rama gh-pages..."
    git checkout --orphan gh-pages
    git rm -rf .
    git checkout main -- frontend/*
fi

# Mover archivos del frontend a la raíz
echo "📂 Moviendo archivos..."
if [ -d "frontend" ]; then
    mv frontend/* .
    rm -rf frontend
fi

# Crear archivo .nojekyll para GitHub Pages
touch .nojekyll

# Commitear
echo "💾 Commiteando cambios..."
git add .
git commit -m "Deploy frontend - $(date '+%Y-%m-%d %H:%M:%S')"

# Push a GitHub
echo "📤 Subiendo a GitHub..."
git push origin gh-pages --force

# Volver a main
echo "🔄 Volviendo a main..."
git checkout main

echo ""
echo "✅ ¡Despliegue completado!"
echo ""
echo "Tu frontend estará disponible en unos minutos en:"
echo "https://$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/' | cut -d'/' -f1).github.io/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/' | cut -d'/' -f2)/"
echo ""
echo "Podés verificar el estado en: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/settings/pages"
