# Apartments Prices (Warsaw) — Python + SQL

Warsaw apartment price analysis using Python, DuckDB, and Streamlit.

## 📋 Requirements

- Python 3.11+
- Conda/Miniconda
- 2GB RAM
- 500MB disk space

## 🚀 Setup

### Quick setup (recommended)

One command does everything: creates environment, installs packages, builds database, and verifies setup.

**Windows:**
```bash
setup_windows.bat
```

**Linux/macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

What it does:
1. Creates conda environment from `environment.yml`
2. Activates environment
3. Installs `apartments` package
4. Builds DuckDB database from CSV files
5. Verifies everything works

Then just run:
```bash
conda activate apartments
streamlit run streamlit_app/app.py
```

### Manual setup

### 1. Create environment

```bash
conda env create -f environment.yml
conda activate apartments
```

### 2. Install package

```bash
pip install -e .
```

### 3. Prepare data

Raw data should be located in:
- `data/raw/sale/*.csv` - sale listings
- `data/raw/rent/*.csv` - rental listings

### 4. Build database

```bash
python scripts/build_db.py
```

This creates `data/processed/apartments.duckdb` with:
- Cleaned data
- Static views (deduplicated)
- Analytical views (time series)

### 5. Verify setup

```bash
python verify_setup.py
```

This script checks:
- ✅ All packages installed
- ✅ `apartments` package available
- ✅ Directory structure
- ✅ Database accessibility

## 📊 Usage

### Streamlit Dashboard

```bash
streamlit run streamlit_app/app.py
```

Available pages:
- **Sale** - sale price analysis
- **Rent** - rental price analysis
- **Yield** - rental yield analysis (proxy)
- **Time Series** - monthly trends

### Jupyter Notebooks

```bash
jupyter lab
```

Notebooks:
- `notebooks/eda_static.ipynb` - static data exploration
- `notebooks/eda_ts.ipynb` - time series analysis

## 📁 Project Structure

```
├── data/
│   ├── raw/              # Raw CSV data
│   ├── processed/        # apartments.duckdb
│   └── reference/        # warsaw_districts.geojson
├── src/apartments/       # Main Python package
│   ├── cleaning.py       # Data cleaning
│   ├── fingerprint.py    # Deduplication
│   ├── io.py             # Data loading
│   ├── labels.py         # Label mappings
│   ├── location.py       # Geocoding
│   ├── rental_yield.py   # Yield calculations
│   └── viz.py            # Plotly visualizations
├── streamlit_app/        # Streamlit dashboard
│   ├── app.py            # Main app
│   ├── components/       # UI components
│   │   ├── loaders.py    # DuckDB loaders
│   │   ├── sidebar.py    # Filters
│   │   └── ui.py         # CSS and components
│   └── pages/            # Dashboard pages
│       ├── 1_Sale.py
│       ├── 2_Rent.py
│       ├── 3_Yield.py
│       └── 4_Time_Series.py
├── scripts/              # Processing scripts
│   ├── build_db.py       # Database build
│   └── build_dataset.py  # Data preparation
├── tests/                # Tests
├── environment.yml       # Conda environment
├── setup.py              # Package installation
└── README.md             # This file
```

## 🔧 Development

### Run tests

```bash
pytest tests/
```

### Rebuild database

```bash
python scripts/build_db.py
```

### Format code

```bash
black src/ streamlit_app/ scripts/
```

## 📦 Main Dependencies

- **pandas** 2.0+ - data manipulation
- **numpy** 1.24+ - numerical operations
- **duckdb** - analytical database
- **streamlit** 1.30+ - interactive dashboard
- **plotly** 5.17+ - interactive visualizations
- **scikit-learn** 1.3+ - machine learning
- **geopandas** - geospatial operations
- **statsmodels** - statistical models

## 📈 Features

### Streamlit Dashboard
- **Dynamic filters**: district, price, area, floor, build year
- **KPI with trends**: month-over-month comparison
- **Visualizations**:
  - Price distribution histograms
  - Boxplots by category
  - Price vs. area scatter plots
  - Yield bar charts
  - Time series line charts
- **Smart binning**: floors, build year
- **Readable labels**: Polish district names and categories

### Database
- **Deduplication**: remove duplicates within month
- **Fingerprinting**: unique property identification
- **Static views**: one listing per property
- **Time series views**: monthly aggregations
- **Yield proxy**: rent/price ratio calculations

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
```bash
pip install -e .
```

### Issue: No data in dashboard
```bash
python scripts/build_db.py
```

### Issue: DuckDB loading error
Check if `data/processed/apartments.duckdb` file exists.
## 📚 Documentation

- **[README.md](README.md)** - This file, main overview
- **[COMMANDS.md](COMMANDS.md)** - All available commands and usage
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Developer guide
- **[requirements.txt](requirements.txt)** - Pip dependencies
- **[environment.yml](environment.yml)** - Conda environment

## 🛠️ Helper Scripts

- **verify_setup.py** - Installation verification
- **setup_windows.bat** - Automated setup (Windows)
- **setup.sh** - Automated setup (Linux/macOS)
## 📝 License

Educational and analytical purposes

