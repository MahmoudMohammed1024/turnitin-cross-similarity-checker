@echo off
title Turnitin Academic Cross-Similarity Checker
cd /d "%~dp0"
cls
echo ====================================================================
echo   Turnitin Academic Cross-Similarity ^& Plagiarism Engine
echo ====================================================================
echo.
echo [*] Starting local server on http://localhost:5000 ...
echo [*] Opening your browser automatically...
start "" http://localhost:5000
echo.
echo [OK] Server is running! Keep this window open while using the website.
echo      To stop the server, simply close this black window.
echo ====================================================================
echo.
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] An error occurred while starting the server.
    pause
)
