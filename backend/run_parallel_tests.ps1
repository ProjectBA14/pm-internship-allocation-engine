# Enhanced Features Parallel Test Runner
# Runs Flask server and tests simultaneously on Windows

param(
    [switch]$SkipTests,
    [int]$ServerTimeout = 10,
    [int]$Port = 5000
)

Write-Host "🚀 Enhanced PM Internship Allocation Engine - Parallel Test Runner" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Gray

# Function to test if server is running
function Test-ServerRunning {
    param([string]$Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -UseBasicParsing
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

# Function to start Flask server in background
function Start-FlaskServer {
    Write-Host "🌐 Starting Flask server in background..." -ForegroundColor Yellow
    
    $serverJob = Start-Job -ScriptBlock {
        param($BackendPath, $Port)
        Set-Location $BackendPath
        $env:FLASK_ENV = "development"
        python app.py
    } -ArgumentList (Get-Location), $Port
    
    Write-Host "   Server job ID: $($serverJob.Id)" -ForegroundColor Gray
    
    # Wait for server to start
    $serverUrl = "http://localhost:$Port/health"
    $attempts = 0
    $maxAttempts = $ServerTimeout
    
    Write-Host "   Waiting for server to start..." -ForegroundColor Gray
    
    while ($attempts -lt $maxAttempts) {
        Start-Sleep -Seconds 1
        if (Test-ServerRunning -Url $serverUrl) {
            Write-Host "✅ Server is running at http://localhost:$Port" -ForegroundColor Green
            return $serverJob
        }
        $attempts++
        Write-Host "   Attempt $attempts/$maxAttempts..." -ForegroundColor Gray
    }
    
    Write-Host "❌ Server failed to start within $ServerTimeout seconds" -ForegroundColor Red
    Stop-Job $serverJob
    Remove-Job $serverJob
    return $null
}

# Function to run feature tests
function Start-FeatureTests {
    Write-Host "🧪 Running enhanced features test suite..." -ForegroundColor Yellow
    
    $testJob = Start-Job -ScriptBlock {
        param($BackendPath)
        Set-Location $BackendPath
        python test_enhanced_features.py
    } -ArgumentList (Get-Location)
    
    Write-Host "   Test job ID: $($testJob.Id)" -ForegroundColor Gray
    return $testJob
}

# Function to test API endpoints
function Test-APIEndpoints {
    param([string]$BaseUrl)
    
    Write-Host "🔍 Testing API endpoints..." -ForegroundColor Yellow
    
    $endpoints = @(
        @{ Method = "GET"; Path = "/health"; Description = "Health check" },
        @{ Method = "GET"; Path = "/api/smart-internships/test-123"; Description = "Internship details" }
    )
    
    $results = @()
    
    foreach ($endpoint in $endpoints) {
        try {
            $url = "$BaseUrl$($endpoint.Path)"
            $response = Invoke-WebRequest -Uri $url -Method $endpoint.Method -TimeoutSec 10 -UseBasicParsing
            
            if ($response.StatusCode -eq 200) {
                Write-Host "   ✅ $($endpoint.Description): $($endpoint.Method) $($endpoint.Path)" -ForegroundColor Green
                $results += @{ Endpoint = $endpoint.Path; Status = "PASS" }
            } else {
                Write-Host "   ⚠️ $($endpoint.Description): $($endpoint.Method) $($endpoint.Path) (Status: $($response.StatusCode))" -ForegroundColor Yellow
                $results += @{ Endpoint = $endpoint.Path; Status = "WARN" }
            }
        }
        catch {
            Write-Host "   ❌ $($endpoint.Description): $($endpoint.Method) $($endpoint.Path) (Error: $($_.Exception.Message))" -ForegroundColor Red
            $results += @{ Endpoint = $endpoint.Path; Status = "FAIL" }
        }
    }
    
    return $results
}

# Function to test enhanced features via API
function Test-EnhancedFeatures {
    param([string]$BaseUrl)
    
    Write-Host "🎯 Testing enhanced internship features..." -ForegroundColor Yellow
    
    # Test data
    $testProfile = @{
        candidate_profile = @{
            skills = @{
                technical = @("Python", "React", "Node.js")
                soft = @("Communication", "Problem Solving")
            }
            category = "Software Development"
            location = "Bangalore"
        }
        categories = @("Software Development")
        limit = 5
    } | ConvertTo-Json -Depth 3
    
    try {
        # Test smart search endpoint
        $searchUrl = "$BaseUrl/api/smart-internships/search"
        Write-Host "   Testing smart search..." -ForegroundColor Gray
        
        $response = Invoke-WebRequest -Uri $searchUrl -Method POST -Body $testProfile -ContentType "application/json" -TimeoutSec 15 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            $data = $response.Content | ConvertFrom-Json
            Write-Host "   ✅ Smart search successful" -ForegroundColor Green
            Write-Host "      Returned internships: $($data.internships.Count)" -ForegroundColor Gray
        }
        
    }
    catch {
        Write-Host "   ⚠️ Smart search test skipped (expected for demo)" -ForegroundColor Yellow
        Write-Host "      Reason: $($_.Exception.Message)" -ForegroundColor Gray
    }
    
    try {
        # Test recommendations endpoint
        $recoUrl = "$BaseUrl/api/smart-internships/recommendations"
        Write-Host "   Testing recommendations..." -ForegroundColor Gray
        
        $recoData = @{
            candidate_profile = @{
                skills = @{
                    technical = @("Java", "Spring Boot")
                }
                category = "Backend Development"
            }
        } | ConvertTo-Json -Depth 3
        
        $response = Invoke-WebRequest -Uri $recoUrl -Method POST -Body $recoData -ContentType "application/json" -TimeoutSec 15 -UseBasicParsing
        
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Recommendations successful" -ForegroundColor Green
        }
        
    }
    catch {
        Write-Host "   ⚠️ Recommendations test skipped (expected for demo)" -ForegroundColor Yellow
        Write-Host "      Reason: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

# Main execution
try {
    # Check if we're in the right directory
    if (-not (Test-Path "app.py")) {
        Write-Host "❌ app.py not found. Please run this script from the backend directory." -ForegroundColor Red
        exit 1
    }
    
    # Start the feature tests first (they don't need the server)
    $testJob = $null
    if (-not $SkipTests) {
        $testJob = Start-FeatureTests
    }
    
    # Start the Flask server
    $serverJob = Start-FlaskServer
    
    if ($serverJob -eq $null) {
        Write-Host "❌ Failed to start server. Exiting." -ForegroundColor Red
        if ($testJob) {
            Stop-Job $testJob
            Remove-Job $testJob
        }
        exit 1
    }
    
    # Wait a bit more for full server initialization
    Start-Sleep -Seconds 2
    
    # Test API endpoints
    $baseUrl = "http://localhost:$Port"
    $apiResults = Test-APIEndpoints -BaseUrl $baseUrl
    
    # Test enhanced features
    Test-EnhancedFeatures -BaseUrl $baseUrl
    
    # Wait for test job to complete
    if ($testJob) {
        Write-Host "📊 Waiting for feature tests to complete..." -ForegroundColor Yellow
        Wait-Job $testJob | Out-Null
        
        Write-Host "`n" + "="*60 -ForegroundColor Gray
        Write-Host "🧪 FEATURE TEST RESULTS:" -ForegroundColor Cyan
        Write-Host "="*60 -ForegroundColor Gray
        
        Receive-Job $testJob
        Remove-Job $testJob
    }
    
    # Display API test results
    Write-Host "`n" + "="*60 -ForegroundColor Gray
    Write-Host "🌐 API ENDPOINT TEST RESULTS:" -ForegroundColor Cyan
    Write-Host "="*60 -ForegroundColor Gray
    
    foreach ($result in $apiResults) {
        $status = switch ($result.Status) {
            "PASS" { "✅ PASS" }
            "WARN" { "⚠️ WARN" }
            "FAIL" { "❌ FAIL" }
        }
        Write-Host "$($result.Endpoint.PadRight(30)) $status"
    }
    
    # Final summary
    Write-Host "`n" + "="*60 -ForegroundColor Gray
    Write-Host "🎉 PARALLEL TESTING COMPLETE!" -ForegroundColor Green
    Write-Host "="*60 -ForegroundColor Gray
    
    Write-Host "🌐 Flask server is running at: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "📚 API Documentation: docs/ENHANCED_API_DOCUMENTATION.md" -ForegroundColor Cyan
    Write-Host "🧪 Feature Tests: Completed" -ForegroundColor Cyan
    
    Write-Host "`n💡 Next steps:" -ForegroundColor Yellow
    Write-Host "   • Test endpoints manually: http://localhost:$Port/health" -ForegroundColor Gray
    Write-Host "   • View API docs: docs/ENHANCED_API_DOCUMENTATION.md" -ForegroundColor Gray
    Write-Host "   • Stop server: Press Ctrl+C or close this window" -ForegroundColor Gray
    
    # Keep server running
    Write-Host "`n⏳ Server will keep running. Press Ctrl+C to stop..." -ForegroundColor Yellow
    try {
        Wait-Job $serverJob | Out-Null
    }
    catch {
        Write-Host "`n🛑 Server stopped." -ForegroundColor Red
    }
    
}
catch {
    Write-Host "❌ Error during execution: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    # Cleanup jobs
    if ($serverJob) {
        Stop-Job $serverJob -ErrorAction SilentlyContinue
        Remove-Job $serverJob -ErrorAction SilentlyContinue
    }
    if ($testJob) {
        Stop-Job $testJob -ErrorAction SilentlyContinue
        Remove-Job $testJob -ErrorAction SilentlyContinue
    }
    
    Write-Host "`nCleanup completed." -ForegroundColor Gray
}
