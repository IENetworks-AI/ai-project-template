#!/bin/bash

echo "🚀 Starting AI Project Application..."

# Navigate to project directory
cd ~/ai-project-template

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Start the application
echo "🚀 Starting Flask application..."
python3 app.py 