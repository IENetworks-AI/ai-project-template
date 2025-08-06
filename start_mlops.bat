@echo off
setlocal enabledelayedexpansion

REM MLOps Pipeline Startup Script for Windows
REM This script starts the entire MLOps environment and performs health checks

echo ⚽ Starting Real-time Football Match Prediction MLOps Pipeline
echo ================================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] docker-compose is not installed. Please install it and try again.
    pause
    exit /b 1
)

echo [INFO] Starting MLOps services...

REM Stop any existing services
echo [INFO] Stopping existing services...
docker-compose down --remove-orphans

REM Start services
echo [INFO] Starting services with docker-compose...
docker-compose up -d

REM Wait for services to be ready
echo [INFO] Waiting for services to be ready...

REM Wait for Zookeeper
timeout /t 10 /nobreak >nul
echo [INFO] Checking Zookeeper...
docker-compose exec -T zookeeper echo "Zookeeper is running" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Zookeeper failed to start
    pause
    exit /b 1
)
echo [SUCCESS] Zookeeper is running

REM Wait for Kafka
echo [INFO] Waiting for Kafka to be ready...
set /a attempts=0
:wait_for_kafka
set /a attempts+=1
docker-compose exec -T kafka kafka-topics --bootstrap-server localhost:9092 --list >nul 2>&1
if errorlevel 1 (
    if !attempts! lss 30 (
        echo [WARNING] Kafka not ready yet (attempt !attempts!/30)
        timeout /t 2 /nobreak >nul
        goto wait_for_kafka
    ) else (
        echo [ERROR] Kafka failed to start after 30 attempts
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] Kafka is ready!
)

REM Create Kafka topic if it doesn't exist
echo [INFO] Creating Kafka topic...
docker-compose exec -T kafka kafka-topics --create --bootstrap-server localhost:9092 --topic live_football_events --partitions 1 --replication-factor 1 --if-not-exists
echo [SUCCESS] Kafka topic 'live_football_events' created/verified

REM Wait for Airflow to be ready
echo [INFO] Waiting for Airflow to be ready...
timeout /t 30 /nobreak >nul

REM Wait for API to be ready
echo [INFO] Waiting for Model API to be ready...
timeout /t 20 /nobreak >nul

REM Wait for Dashboard to be ready
echo [INFO] Waiting for Dashboard to be ready...
timeout /t 15 /nobreak >nul

REM Display service information
echo.
echo 🎉 MLOps Pipeline is ready!
echo ================================================================
echo.
echo 📊 Service URLs:
echo    • Airflow UI:        http://localhost:8080
echo    • Model API:         http://localhost:8000
echo    • API Docs:          http://localhost:8000/docs
echo    • Dashboard:         http://localhost:8501
echo    • Kafka:             localhost:9092
echo.
echo 🔧 Useful Commands:
echo    • View logs:         docker-compose logs -f
echo    • Stop services:     docker-compose down
echo    • Restart services:  docker-compose restart
echo    • Check status:      docker-compose ps
echo.
echo 📈 Next Steps:
echo    1. Open the Dashboard at http://localhost:8501
echo    2. Start the data producer: python producer/producer.py
echo    3. Monitor the pipeline in Airflow at http://localhost:8080
echo    4. Test the API: curl http://localhost:8000/health
echo.
echo 🚀 Happy predicting! ⚽
echo.

REM Optional: Start the producer automatically
set /p start_producer="Would you like to start the data producer now? (y/n): "
if /i "!start_producer!"=="y" (
    echo [INFO] Starting data producer...
    python producer/producer.py --kafka-broker localhost:9092 --delay 1.0 --max-events 50
)

pause 