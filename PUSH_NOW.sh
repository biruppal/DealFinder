#!/bin/bash

# DealFinder - Quick Push to GitHub Script
# Run this to immediately push to GitHub

echo "🚀 DealFinder - Push to GitHub"
echo "================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git not installed. Please install git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Not in DealFinder directory. Please cd to the project root."
    exit 1
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Add all files
echo "📝 Adding all files..."
git add .
echo "✅ Files added"

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: DealFinder AI-powered deal analyzer

- Core Claude agent with vision + tool use
- FastAPI backend with comprehensive API
- PostgreSQL database with ORM models
- Docker containerization
- GitHub Actions CI/CD pipeline
- Comprehensive documentation
- 80%+ test coverage"

echo "✅ Initial commit created"

# Check for remote
if ! git remote get-url origin &> /dev/null; then
    echo ""
    echo "📌 NO GITHUB REMOTE SET YET"
    echo ""
    echo "1. Go to GitHub: https://github.com/new"
    echo "2. Create new repository: 'DealFinder'"
    echo "3. Then run this command:"
    echo ""
    echo "   git remote add origin https://github.com/YOUR_USERNAME/DealFinder.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
else
    echo "🔄 Pushing to GitHub..."
    git branch -M main
    git push -u origin main
    echo "✅ Pushed to GitHub!"
    echo ""
    echo "🎉 Your project is now on GitHub!"
    echo "📍 View at: https://github.com/biruppal/DealFinder"
fi
