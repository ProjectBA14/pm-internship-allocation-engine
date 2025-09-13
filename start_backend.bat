@echo off
echo Starting PM Internship Allocation Engine Backend Server...
cd /d "C:\Users\aksha\pm-internship-allocation-engine\backend"
echo Backend server starting on http://localhost:5000
python -m flask --app app run --host=0.0.0.0 --port=5000
pause
