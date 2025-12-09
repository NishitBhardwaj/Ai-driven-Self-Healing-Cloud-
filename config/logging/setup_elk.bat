@echo off
REM Setup script for ELK Stack on Windows

echo ==========================================
echo ELK Stack Setup
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo Starting ELK Stack...
cd /d "%~dp0"

REM Start ELK Stack
docker-compose -f elk-docker-compose.yml up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ==========================================
echo ELK Stack is starting!
echo ==========================================
echo.
echo Elasticsearch: http://localhost:9200
echo Kibana: http://localhost:5601
echo Logstash: TCP localhost:5000, UDP localhost:5001
echo.
echo Next steps:
echo 1. Open Kibana at http://localhost:5601
echo 2. Create index pattern: agent-logs-*
echo 3. Import dashboards from config/logging/kibana-dashboards/
echo 4. Configure agents to send logs to Logstash
echo.

pause

