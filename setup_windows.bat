@echo off
REM Quick setup script for Windows users

echo ============================================================
echo APARTMENTS PROJECT - QUICK SETUP
echo ============================================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Conda not found. Please install Miniconda or Anaconda first.
    echo Download from: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo Step 1: Creating conda environment...
call conda env create -f environment.yml
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create environment
    pause
    exit /b 1
)
echo   [OK] Environment created
echo.

echo Step 2: Activating environment...
call conda activate apartments
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate environment
    pause
    exit /b 1
)
echo   [OK] Environment activated
echo.

echo Step 3: Installing package in development mode...
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install package
    pause
    exit /b 1
)
echo   [OK] Package installed
echo.

echo Step 4: Building database from CSV files...
python scripts/build_db.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build database
    pause
    exit /b 1
)
echo   [OK] Database created
echo.

echo Step 5: Verifying setup...
python verify_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Some checks failed
    pause
    exit /b 1
)
echo.

echo ============================================================
echo SUCCESS! Setup completed successfully.
echo.
echo To start the dashboard, run:
echo   conda activate apartments
echo   streamlit run streamlit_app/app.py
echo ============================================================
pause
