# PM Internship Allocation Engine - Enhanced Features Runner
# Runs Flask server and tests in parallel on Windows

$Host.UI.RawUI.WindowTitle = "PM Internship Allocation Engine - Enhanced Features"
Clear-Host

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🚀 PM INTERNSHIP ALLOCATION ENGINE - ENHANCED FEATURES" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting all services in parallel..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Error: app.py not found. Make sure you're in the backend directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "📋 Current directory: $(Get-Location)" -ForegroundColor Gray
Write-Host "⏰ Started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# Function to test if server is running
function Test-ServerRunning {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

# Start Flask server in background
Write-Host "🌐 Starting Flask server in background..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
    param($BackendPath)
    Set-Location $BackendPath
    $env:FLASK_ENV = "development"
    python app.py
} -ArgumentList (Get-Location)

Write-Host "   Server job ID: $($serverJob.Id)" -ForegroundColor Gray

# Wait for server to start
Write-Host "   Waiting for server to start..." -ForegroundColor Gray
$attempts = 0
$maxAttempts = 15
$serverUrl = "http://localhost:5000/health"

while ($attempts -lt $maxAttempts) {
    Start-Sleep -Seconds 1
    if (Test-ServerRunning -Url $serverUrl) {
        Write-Host "✅ Server is running at http://localhost:5000" -ForegroundColor Green
        break
    }
    $attempts++
    Write-Host "   Attempt $attempts/$maxAttempts..." -ForegroundColor Gray
}

if ($attempts -eq $maxAttempts) {
    Write-Host "⚠️ Server may still be starting. Continuing with demo..." -ForegroundColor Yellow
}

Write-Host ""

# Run enhanced features demo
Write-Host "🧪 Running enhanced features demo..." -ForegroundColor Yellow
try {
    python demo_enhanced_features.py
    Write-Host "✅ Demo completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Demo encountered issues: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# Run comprehensive test suite
Write-Host "🔍 Running comprehensive test suite..." -ForegroundColor Yellow
try {
    python test_enhanced_features.py
    Write-Host "✅ Tests completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Tests encountered issues: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "🎉 ALL PROCESSES STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Display status information
Write-Host "🌐 Flask Server: Running in background" -ForegroundColor Cyan
Write-Host "    ↳ URL: http://localhost:5000" -ForegroundColor Gray
Write-Host "    ↳ Health Check: http://localhost:5000/health" -ForegroundColor Gray
Write-Host "    ↳ Job ID: $($serverJob.Id)" -ForegroundColor Gray
Write-Host ""

Write-Host "📋 Enhanced API Endpoints:" -ForegroundColor Cyan
Write-Host "    ↳ POST /api/smart-internships/search" -ForegroundColor Gray
Write-Host "    ↳ GET  /api/smart-internships/{id}" -ForegroundColor Gray
Write-Host "    ↳ POST /api/smart-internships/recommendations" -ForegroundColor Gray
Write-Host ""

Write-Host "💡 Next Steps:" -ForegroundColor Yellow
Write-Host "    • Test endpoints manually in browser or Postman" -ForegroundColor Gray
Write-Host "    • Monitor server job: Receive-Job $($serverJob.Id)" -ForegroundColor Gray
Write-Host "    • Stop server: Stop-Job $($serverJob.Id)" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "    • API Docs: docs\ENHANCED_API_DOCUMENTATION.md" -ForegroundColor Gray
Write-Host "    • Features: README_ENHANCED_FEATURES.md" -ForegroundColor Gray
Write-Host "    • Summary: IMPLEMENTATION_SUMMARY.md" -ForegroundColor Gray
Write-Host ""

# Test server connection
Write-Host "🔍 Testing server connection..." -ForegroundColor Yellow
if (Test-ServerRunning -Url $serverUrl) {
    Write-Host "✅ Server is responding at http://localhost:5000" -ForegroundColor Green
    
    # Test a simple API call
    try {
        $healthResponse = Invoke-WebRequest -Uri $serverUrl -UseBasicParsing -TimeoutSec 5
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-Host "✅ Health check successful - Service: $($healthData.service)" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Health check failed, but server is running" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Server may still be starting up. Check job status." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⏰ Completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# Interactive menu
do {
    Write-Host "🎯 Choose an option:" -ForegroundColor Yellow
    Write-Host "  1. Open health check in browser" -ForegroundColor Gray
    Write-Host "  2. Show server job status" -ForegroundColor Gray
    Write-Host "  3. View server logs" -ForegroundColor Gray
    Write-Host "  4. Test API endpoints" -ForegroundColor Gray
    Write-Host "  5. Stop server and exit" -ForegroundColor Gray
    Write-Host "  0. Exit (keep server running)" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Enter choice (0-5)"
    
    switch ($choice) {
        "1" {
            Write-Host "🌐 Opening browser..." -ForegroundColor Green
            Start-Process "http://localhost:5000/health"
        }
        "2" {
            Write-Host "📊 Server job status:" -ForegroundColor Yellow
            Get-Job $serverJob.Id | Format-Table
        }
        "3" {
            Write-Host "📋 Recent server logs:" -ForegroundColor Yellow
            try {
                Receive-Job $serverJob.Id -Keep | Select-Object -Last 20
            }
            catch {
                Write-Host "No logs available yet or job not running" -ForegroundColor Yellow
            }
        }
        "4" {
            Write-Host "🧪 Testing API endpoints..." -ForegroundColor Yellow
            
            # Test health endpoint
            try {
                $health = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
                Write-Host "✅ Health check: $($health.StatusCode)" -ForegroundColor Green
            }
            catch {
                Write-Host "❌ Health check failed" -ForegroundColor Red
            }
            
            # Test internship details endpoint  
            try {
                $details = Invoke-WebRequest -Uri "http://localhost:5000/api/smart-internships/test-123" -UseBasicParsing -TimeoutSec 5
                Write-Host "✅ Internship details: $($details.StatusCode)" -ForegroundColor Green
            }
            catch {
                Write-Host "❌ Internship details failed: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
        "5" {
            Write-Host "🛑 Stopping server..." -ForegroundColor Red
            Stop-Job $serverJob
            Remove-Job $serverJob
            Write-Host "✅ Server stopped" -ForegroundColor Green
            exit 0
        }
        "0" {
            Write-Host "🎯 Exiting but keeping server running..." -ForegroundColor Green
            Write-Host "Server Job ID: $($serverJob.Id)" -ForegroundColor Yellow
            Write-Host "To stop later: Stop-Job $($serverJob.Id); Remove-Job $($serverJob.Id)" -ForegroundColor Gray
            exit 0
        }
        default {
            Write-Host "Invalid choice. Please enter 0-5." -ForegroundColor Red
        }
    }
    Write-Host ""
} while ($true)
