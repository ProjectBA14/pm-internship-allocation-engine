Write-Host "Starting PM Internship Allocation Engine Backend Server..." -ForegroundColor Green
Set-Location "C:\Users\aksha\pm-internship-allocation-engine\backend"

Write-Host "Backend server starting on http://localhost:5000" -ForegroundColor Yellow
Write-Host "Server is running in the background. Check the Flask output for status." -ForegroundColor Cyan

# Start the Flask server in the background
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m","flask","--app","app","run","--host=0.0.0.0","--port=5000"

Write-Host "Backend server started successfully!" -ForegroundColor Green
Write-Host "You can now run the frontend with: npm start" -ForegroundColor Yellow
