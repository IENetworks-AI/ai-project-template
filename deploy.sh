
#!/bin/bash
set -e  # Exit on any error

echo "🔄 Starting deployment..."

cd ~/ai-project-template

echo "📥 Pulling latest code..."
git pull origin main

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "✅ Activating virtual environment..."
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

if [ -f "app.py" ]; then
    echo "🚀 Running app.py in background..."
    pkill -f app.py || true    # kill previous if running
    nohup python3 app.py > output.log 2>&1 &
    echo "✅ App is running."
else
    echo "⚠️ app.py not found."
fi

echo "✅ Deployment finished."
