@echo off
REM SIEA Development Environment Start Script for Windows

echo 🚀 SIEA Development Environment Starting...

REM Check if Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Start development services
echo 📦 Starting development services...
docker-compose -f docker-compose.dev.yml up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo ✅ Services status:
docker-compose -f docker-compose.dev.yml ps

echo.
echo 🎉 Development environment is ready!
echo.
echo 📋 Service URLs:
echo    PostgreSQL: localhost:5433
echo    Redis: localhost:6380
echo    pgAdmin: http://localhost:5050 (admin@siea.local / admin)
echo.
echo 📝 Next steps:
echo 1. Start backend: cd backend && python main.py
echo 2. Start frontend: cd frontend && npm start
echo.
echo To stop services: docker-compose -f docker-compose.dev.yml down

pause
