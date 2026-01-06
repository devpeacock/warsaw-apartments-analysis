#!/bin/bash
# Quick setup script for Unix-like systems (Linux, macOS)

echo "============================================================"
echo "APARTMENTS PROJECT - QUICK SETUP"
echo "============================================================"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: Conda not found. Please install Miniconda or Anaconda first."
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "Step 1: Creating conda environment..."
conda env create -f environment.yml
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create environment"
    exit 1
fi
echo "  [OK] Environment created"
echo ""

echo "Step 2: Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate apartments
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate environment"
    exit 1
fi
echo "  [OK] Environment activated"
echo ""

echo "Step 3: Installing package in development mode..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install package"
    exit 1
fi
echo "  [OK] Package installed"
echo ""

echo "Step 4: Building database from CSV files..."
python scripts/build_db.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to build database"
    exit 1
fi
echo "  [OK] Database created"
echo ""

echo "Step 5: Verifying setup..."
python verify_setup.py
if [ $? -ne 0 ]; then
    echo "WARNING: Some checks failed"
    exit 1
fi
echo ""

echo "============================================================"
echo "SUCCESS! Setup completed successfully."
echo ""
echo "To start the dashboard, run:"
echo "  conda activate apartments"
echo "  streamlit run streamlit_app/app.py"
echo "============================================================"
