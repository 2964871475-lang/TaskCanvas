@echo off
cd /d E:\TaskCanvas\frontend
echo Installing dependencies...
npm install
echo Building frontend...
npm run build
echo Build complete: frontend/dist/
pause
