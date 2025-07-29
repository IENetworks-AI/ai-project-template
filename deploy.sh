#!/bin/bash

set -e  # Exit immediately if a command fails

echo "🔄 Starting deployment..."

# 1. Navigate to the project directory
cd ~/ai-project-template

# 2. Pull latest code from GitHub
echo "📥 Pulling latest code..."
git pull origin main

# 3. Activate virtual environment (or create if missing)
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

# 4. Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️ No requirements.txt found. Skipping pip install."
fi

# 5. Optional: Run your model server (adjust this based on your project)
# You can use uvicorn, flask, or any other method your app uses
# Example using Flask:
if [ -f "app.py" ]; then
    echo "🚀 Running your Python app (app.py)..."
    nohup python app.py > output.log 2>&1 &
    echo "✅ App launched and running in background (output.log)"
else
    echo "⚠️ No app.py found to run."
fi

echo "✅ Deployment completed."
