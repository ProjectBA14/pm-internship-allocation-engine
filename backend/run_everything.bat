@echo off
title PM Internship Allocation Engine - Enhanced Features
cls

echo ================================================================
echo 🚀 PM INTERNSHIP ALLOCATION ENGINE - ENHANCED FEATURES
echo ================================================================
echo.
echo Starting all services in parallel...
echo.

REM Change to backend directory
cd /d "%~dp0"

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: app.py not found. Make sure you're in the backend directory.
    pause
    exit /b 1
)

echo 📋 Current directory: %CD%
echo ⏰ Started at: %DATE% %TIME%
echo.

REM Start Flask server in background
echo 🌐 Starting Flask server in background...
start "Flask Server" /min cmd /k "python app.py"

REM Wait a moment for server to start
timeout /t 5 /nobreak > nul

REM Run the enhanced features demo
echo 🧪 Running enhanced features demo...
python demo_enhanced_features.py

echo.
echo 🔍 Running comprehensive test suite...
python test_enhanced_features.py

echo.
echo ================================================================
echo 🎉 ALL PROCESSES STARTED SUCCESSFULLY!
echo ================================================================
echo.
echo 🌐 Flask Server: Running in background (minimized window)
echo    ↳ URL: http://localhost:5000
echo    ↳ Health Check: http://localhost:5000/health
echo.
echo 📋 Enhanced API Endpoints:
echo    ↳ POST /api/smart-internships/search
echo    ↳ GET  /api/smart-internships/{id}
echo    ↳ POST /api/smart-internships/recommendations
echo.
echo 💡 Next Steps:
echo    • Test endpoints manually in browser or Postman
echo    • Check Flask server window for logs
echo    • Press Ctrl+C in Flask window to stop server
echo.
echo 📚 Documentation:
echo    • API Docs: docs\ENHANCED_API_DOCUMENTATION.md
echo    • Features: README_ENHANCED_FEATURES.md
echo    • Summary: IMPLEMENTATION_SUMMARY.md
echo.
echo ⏰ Completed at: %DATE% %TIME%
echo.

REM Test if server is responding
echo 🔍 Testing server connection...
curl -s http://localhost:5000/health > nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Server is responding at http://localhost:5000
) else (
    echo ⚠️ Server may still be starting up. Check the Flask window.
)

echo.
echo Press any key to open browser and view health check...
pause > nul

REM Open browser to health check
start http://localhost:5000/health

echo.
echo 🎯 All done! Server is running in the background.
echo    Close this window when finished, or use the Flask window to stop server.
echo.
pause
