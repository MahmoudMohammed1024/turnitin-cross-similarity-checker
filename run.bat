@echo off
title Turnitin Internal Cross-Similarity Checker
cd /d "%~dp0"
echo ========================================================
echo   Starting Cross-Similarity & Plagiarism Engine...
echo ========================================================
echo.
python app.py
pause
