# Project Commands

Project-specific commands for Warsaw Apartments Analysis.

---

## Quick Setup

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

## Environment Setup

### Create and activate environment
```bash
conda env create -f environment.yml
conda activate apartments
```

### Install package in development mode
```bash
pip install -e .
```

---

## Data Processing

### Build DuckDB database from CSV files
```bash
python scripts/build_db.py
```

### Build processed parquet datasets
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

### Launch with custom port
```bash
streamlit run streamlit_app/app.py --server.port 8502
```

---

## Testing & Verification

### Run all tests
```bash
pytest
```

### Run specific test
```bash
pytest tests/test_cleaning.py
```

### Verify setup
```bash
python verify_setup.py
```

---

## DuckDB Database Queries

### Open DuckDB CLI
```bash
duckdb data/processed/apartments.duckdb
```

### Query from command line
```bash
duckdb data/processed/apartments.duckdb "SELECT * FROM listings_sale_static LIMIT 10;"
```

### Show all tables
```bash
duckdb data/processed/apartments.duckdb "SHOW TABLES;"
```

### Export table to CSV
```bash
duckdb data/processed/apartments.duckdb "COPY listings_sale_static TO 'output.csv' (HEADER);"
```

---

## Maintenance

### Rebuild database from scratch
```bash
rm data/processed/apartments.duckdb
python scripts/build_dataset.py
python scripts/build_db.py
```

### Update environment dependencies
```bash
conda env update -f environment.yml --prune
pip install -e .
```

### Reinstall everything
```bash
conda env remove -n apartments
conda env create -f environment.yml
conda activate apartments
pip install -e .
python verify_setup.py
```

---

## Quick Reference

Daily workflow:
```bash
conda activate apartments          # Activate environment
streamlit run streamlit_app/app.py # Launch dashboard
python scripts/build_db.py         # Rebuild database (if data changed)
pytest                             # Run tests
```
