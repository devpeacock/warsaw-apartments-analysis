# Apartments Prices (Warsaw) — Python + SQL

Warsaw apartment price analysis using Python, DuckDB, and Streamlit.

## Warsaw Apartments Analytics Dashboard

This project is a **functional analytics platform for the Warsaw residential real estate market**, designed around structured data processing, fast analytical queries, and fully interactive exploration of market dynamics. The focus is on **what the system does**: how data is prepared, queried, filtered, and analyzed in a repeatable and extensible way. This project is built using Python, DuckDB, and Streamlit.

## Overview

### Core Functions

#### Data ingestion and preparation
- Loads raw apartment sale and rental listings.
- Filters data to Warsaw at the preprocessing stage.
- Normalizes numeric attributes such as prices, area, floors, build year, and distances.
- Performs within-month deduplication and cross-month **property fingerprinting** so each apartment appears once in static views.
- Outputs cleaned datasets to Parquet for reproducibility and performance.

#### Analytical storage and aggregation
- Builds DuckDB tables and views optimized for analytical workloads.
- Maintains *static* views (one row per apartment) for cross-sectional analysis.
- Creates monthly city-level marts with counts, medians, percentiles, and averages.
- Derives proxy yield metrics by combining sale and rental aggregates.

#### Filtering and segmentation
- Implements a centralized filtering layer shared across all pages and charts.
- Supports filtering by:
  - district and listing type,
  - total price and price per m²,
  - apartment size and floor structure,
  - build year and building characteristics,
  - distances to points of interest,
  - amenities and accessibility features.
- Filters are applied consistently to both KPIs and visualizations.

#### Market metrics and KPI computation
- Computes core indicators such as:
  - number of active listings,
  - median price per m²,
  - median total price,
  - average apartment size.
- Calculates month-over-month changes using aggregated marts.
- Displays directional trends (up / down / flat) directly in KPI cards.

#### Interactive exploratory analysis
- Distribution analysis using histograms and boxplots.
- **Fully interactive scatter plots**, where the user can select which variable appears on the X-axis (e.g. distance to centre, build year, area).
- **Dynamic boxplots**, where the grouping category can be chosen interactively (e.g. district, listing type, condition).
- All charts update in real time in response to sidebar filters.

---

### Application Pages

- **Sale** — analysis of apartment sale listings, pricing structure, and price drivers.
- **Rent** — analysis of rental listings with analogous metrics and filters.
- **Yield** — proxy yield calculations combining sale and rent data.
- **Time Series** — monthly market evolution based on aggregated marts.

Each page follows the same analytical structure while exposing metrics relevant to its domain.

---

### Architecture

- `src/apartments/` — core data logic (cleaning, feature engineering, analytical helpers).
- DuckDB layer — analytical storage and SQL-based aggregation.
- `streamlit_app/components/` — reusable loaders, sidebar logic, and UI helpers.
- Multipage Streamlit application with shared filtering and visualization logic.

---

### Technology Stack

- **Python**, Pandas, NumPy  
- **DuckDB** for analytical queries  
- **Plotly** for interactive charts  
- **Streamlit** for the application layer  
- Packaged as a `src/`-based Python module (`apartments`)

---

### Scope and Extensibility

The system is designed as a **general analytical framework** that can be extended with forecasting models, yield optimization, or additional cities without changes to the core architecture.

## 📋 Requirements

- Python 3.11+
- Conda/Miniconda
- 2GB RAM
- 500MB disk space

## 🚀 Setup

### Quick setup (recommended)

One command does everything: creates environment, installs packages, builds database, and verifies setup.

**Windows (PowerShell):**
```powershell
.\setup_windows.bat
```

**Windows (CMD):**
```cmd
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

