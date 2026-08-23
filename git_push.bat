@echo off
title Tflow — Push to GitHub to Build APK
echo ============================================================
echo   Tflow GitHub Push Automator
echo ============================================================
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed on your system!
    echo Please install Git from: https://git-scm.com/
    pause
    exit /b
)

:: Prompt user for repo URL
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/repo): "

if "%REPO_URL%"=="" (
    echo [ERROR] Repository URL cannot be empty!
    pause
    exit /b
)

echo.
echo [1/4] Initialising local Git repository...
git init

echo [2/4] Staging files...
git add .

echo [3/4] Commencing commit...
git commit -m "Build Tflow Android APK via GitHub Actions"

echo [4/4] Uploading to GitHub...
git branch -M main
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%
git push -u origin main -f

echo.
echo ============================================================
echo   SUCCESS: Upload complete!
echo.
echo   1. Go to your repository on GitHub.
echo   2. Click the 'Actions' tab.
echo   3. Select the 'Build Android APK' workflow.
echo   4. Once complete, download your APK from the bottom!
echo ============================================================
pause
