# Available Commands Reference

Complete list of all commands available in the Apartments Price Analysis project.

---

## Quick Setup (Recommended)

### Windows
```bash
setup_windows.bat
```

### Mac/Linux
```bash
chmod +x setup.sh
./setup.sh
```

---

## Environment Management

### Create Conda environment
```bash
conda env create -f environment.yml
```

### Activate environment
```bash
conda activate apartments
```

### Deactivate environment
```bash
conda deactivate
```

### Update environment from file
```bash
conda env update -f environment.yml --prune
```

### Remove environment
```bash
conda env remove -n apartments
```

### List all Conda environments
```bash
conda env list
```

### Export current environment
```bash
conda env export > environment_backup.yml
```

### Install from requirements.txt (pip)
```bash
pip install -r requirements.txt
```

---

## Package Management

### Install custom package in development mode
```bash
pip install -e .
```

### Install custom package normally
```bash
pip install .
```

### Uninstall custom package
```bash
pip uninstall apartments
```

### Update single package
```bash
conda update <package_name>
# or
pip install --upgrade <package_name>
```

### List installed packages
```bash
conda list
# or
pip list
```

### Show package information
```bash
conda info <package_name>
# or
pip show <package_name>
```

---

## Data Processing

### Build DuckDB database from CSV files
```bash
python scripts/build_db.py
```

### Build dataset (deprecated, use build_db.py)
```bash
python scripts/build_dataset.py
```

### Analyze duplicates in data
```bash
python scripts/analyze_duplicates.py
```

---

## Running Applications

### Launch Streamlit Dashboard
```bash
streamlit run streamlit_app/app.py
```

### Launch Streamlit with specific port
```bash
streamlit run streamlit_app/app.py --server.port 8502
```

### Launch Streamlit in headless mode (no browser)
```bash
streamlit run streamlit_app/app.py --server.headless true
```

### Launch Streamlit with debugging
```bash
streamlit run streamlit_app/app.py --logger.level=debug
```

---

## Jupyter Notebooks

### Launch Jupyter Lab
```bash
jupyter lab
```

### Launch Jupyter Notebook
```bash
jupyter notebook
```

### Convert notebook to Python script
```bash
jupyter nbconvert --to script notebooks/eda_static.ipynb
```

### Convert notebook to HTML
```bash
jupyter nbconvert --to html notebooks/eda_static.ipynb
```

### Execute notebook from command line
```bash
jupyter nbconvert --to notebook --execute notebooks/eda_static.ipynb
```

---

## Testing

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_cleaning.py
```

### Run tests with verbose output
```bash
pytest -v
```

### Run tests with coverage report
```bash
pytest --cov=src/apartments tests/
```

### Run setup verification
```bash
python tests/00_setup_check.py
```

### Run verification script
```bash
python verify_setup.py
```

---

## Diagnostics

### Check Python version
```bash
python --version
```

### Check Conda version
```bash
conda --version
```

### Check pip version
```bash
pip --version
```

### Show system information
```bash
python -c "import platform; print(platform.platform())"
```

### Check Python executable path
```bash
python -c "import sys; print(sys.executable)"
```

### Check installed package location
```bash
python -c "import apartments; print(apartments.__file__)"
```

### List all Python paths
```bash
python -c "import sys; print('\n'.join(sys.path))"
```

---

## DuckDB Database

### Open DuckDB CLI
```bash
duckdb data/processed/apartments.duckdb
```

### Query database from CLI
```bash
duckdb data/processed/apartments.duckdb "SELECT * FROM listings_sale_static LIMIT 10;"
```

### Export table to CSV
```bash
duckdb data/processed/apartments.duckdb "COPY listings_sale_static TO 'output.csv' (HEADER, DELIMITER ',');"
```

### Show all tables
```bash
duckdb data/processed/apartments.duckdb "SHOW TABLES;"
```

### Describe table schema
```bash
duckdb data/processed/apartments.duckdb "DESCRIBE listings_sale_static;"
```

### Database statistics
```bash
duckdb data/processed/apartments.duckdb "SELECT COUNT(*) FROM listings_sale_static;"
```

---

## Maintenance

### Clean Python cache files
```bash
# Windows PowerShell
Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse

# Mac/Linux
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Clean Jupyter checkpoint files
```bash
# Windows PowerShell
Get-ChildItem -Path . -Include .ipynb_checkpoints -Recurse -Force | Remove-Item -Force -Recurse

# Mac/Linux
find . -type d -name .ipynb_checkpoints -exec rm -rf {} +
```

### Rebuild database from scratch
```bash
# Remove old database
rm data/processed/apartments.duckdb

# Rebuild
python scripts/build_db.py
```

---

## Git Workflow

### Clone repository
```bash
git clone <repository_url>
cd apartments_prices
```

### Create new branch
```bash
git checkout -b feature/new-feature
```

### Stage changes
```bash
git add .
```

### Commit changes
```bash
git commit -m "feat: Add new feature"
```

### Push changes
```bash
git push origin feature/new-feature
```

### Pull latest changes
```bash
git pull origin main
```

### View commit history
```bash
git log --oneline
```

### Show changes
```bash
git diff
```

---

## Environment Variables

### Set Streamlit configuration (Windows)
```powershell
$env:STREAMLIT_SERVER_PORT = "8502"
$env:STREAMLIT_SERVER_HEADLESS = "true"
```

### Set Streamlit configuration (Mac/Linux)
```bash
export STREAMLIT_SERVER_PORT=8502
export STREAMLIT_SERVER_HEADLESS=true
```

### Set Python path (Windows)
```powershell
$env:PYTHONPATH = "$PWD"
```

### Set Python path (Mac/Linux)
```bash
export PYTHONPATH=$(pwd)
```

---

## Monitoring

### Show Streamlit process
```bash
# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*streamlit*"}

# Mac/Linux
ps aux | grep streamlit
```

### Kill Streamlit process (Windows)
```powershell
Stop-Process -Name streamlit -Force
```

### Kill Streamlit process (Mac/Linux)
```bash
pkill -f streamlit
```

### Monitor system resources (Windows)
```powershell
Get-Process -Name python | Select-Object CPU,PM
```

### Monitor system resources (Mac/Linux)
```bash
top -p $(pgrep -f streamlit)
```

---

## Troubleshooting

### Reinstall all dependencies
```bash
conda env remove -n apartments
conda env create -f environment.yml
conda activate apartments
pip install -e .
```

### Clear Streamlit cache
```bash
# Delete cache directory
# Windows
Remove-Item -Path "$HOME\.streamlit\cache" -Recurse -Force

# Mac/Linux
rm -rf ~/.streamlit/cache
```

### Fix import errors
```bash
# Reinstall package
pip uninstall apartments
pip install -e .
```

### Check for missing data files
```bash
python verify_setup.py
```

### Validate database integrity
```bash
python scripts/build_db.py
```

### Reset environment to clean state
```bash
# Remove conda environment
conda env remove -n apartments

# Remove custom package
pip uninstall apartments -y

# Remove cache files
Get-ChildItem -Path . -Include __pycache__,*.pyc -Recurse -Force | Remove-Item -Force -Recurse

# Rebuild everything
conda env create -f environment.yml
conda activate apartments
pip install -e .
python verify_setup.py
```

---

## Documentation

### Generate API documentation (if using Sphinx)
```bash
cd docs
make html
```

### View README in terminal
```bash
# Windows PowerShell
Get-Content README.md

# Mac/Linux
cat README.md
```

### Search for specific text in codebase
```bash
# Windows PowerShell
Select-String -Path "src\**\*.py" -Pattern "function_name"

# Mac/Linux
grep -r "function_name" src/
```

---

## Data Export

### Export filtered data from dashboard
Within Streamlit app:
1. Apply desired filters
2. Use built-in dataframe download (if available)
3. Or query database directly using filters

### Export database view to CSV
```bash
duckdb data/processed/apartments.duckdb "COPY (SELECT * FROM mart_city_month_sale) TO 'sale_trends.csv' (HEADER);"
```

### Export to Excel (using pandas)
```python
import pandas as pd
import duckdb

con = duckdb.connect('data/processed/apartments.duckdb')
df = con.execute("SELECT * FROM listings_sale_static").df()
df.to_excel('export.xlsx', index=False)
```

---

## Performance Optimization

### Profile Python code
```bash
python -m cProfile -o profile_output.prof scripts/build_db.py
```

### Profile memory usage
```bash
python -m memory_profiler scripts/build_db.py
```

### Benchmark database queries
```bash
duckdb data/processed/apartments.duckdb "EXPLAIN ANALYZE SELECT * FROM listings_sale_static WHERE district = 'Mokotów';"
```

---

## Quick Cheat Sheet

Most commonly used commands:

```bash
# Setup (first time)
setup_windows.bat  # or ./setup.sh on Mac/Linux

# Daily workflow
conda activate apartments          # Activate environment
streamlit run streamlit_app/app.py # Launch dashboard
python scripts/build_db.py         # Rebuild database
pytest                             # Run tests
python verify_setup.py             # Verify setup

# Maintenance
conda env update -f environment.yml --prune  # Update packages
pip install -e .                             # Reinstall custom package
```

---

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Documentation](https://plotly.com/python/)
- [Conda Cheat Sheet](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)

---

**Note**: Replace `<package_name>`, `<repository_url>`, and other placeholders with actual values when using these commands.
