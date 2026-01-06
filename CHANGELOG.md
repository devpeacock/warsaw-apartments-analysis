# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-06

### Added
- Initial release of Warsaw Apartments Price Analysis project
- Streamlit multi-page dashboard with 4 main pages:
  - Sale: Analysis of sale listings
  - Rent: Analysis of rental listings  
  - Yield: Rental yield proxy calculations
  - Time Series: Monthly trends visualization
- DuckDB database with optimized views:
  - Static views (deduplicated across months)
  - Time series views (monthly aggregations)
  - Yield proxy calculations
- Interactive filtering system:
  - District selection
  - Price and area ranges
  - Building characteristics (floor, year, material)
  - Property features (rooms, condition, listing type)
  - Amenities (parking, balcony, elevator, security, storage)
  - Distance filters (school, clinic, pharmacy, etc.)
- KPI cards with month-over-month trend indicators
- Custom visualization functions:
  - Histograms with median markers
  - Boxplots by category with natural ordering
  - Scatter plots with trend lines
  - Bar charts for categorical analysis
  - Line charts for time series
- Data processing pipeline:
  - CSV loading and cleaning
  - Fingerprinting for deduplication
  - Geocoding and district assignment
  - Within-month deduplication
  - Cross-month static views
- Binned categories for better analysis:
  - Floor bins (0-5, 5-10, 10-15, 15-20, 20+)
  - Total floors bins (same ranges)
  - Build year bins (pre-1900, 1900-1950, 1950-1980, then 10-year intervals)
- Label mapping system for readable UI:
  - Polish district names
  - Translated property types
  - Human-readable building conditions
- Reproducibility setup:
  - Complete environment.yml with pinned versions
  - requirements.txt for pip users
  - setup.py for package installation
  - Automatic setup scripts (Windows and Unix)
  - Environment verification script
  - Comprehensive documentation

### Documentation
- README.md with complete setup instructions
- CONTRIBUTING.md with development guidelines
- COMMANDS.md with all available commands
- MANIFEST.in for package distribution
- .gitignore for version control

### Technical Stack
- Python 3.11
- pandas 2.0+ for data manipulation
- DuckDB for analytical database
- Streamlit 1.30+ for interactive dashboard
- Plotly 5.17+ for visualizations
- scikit-learn 1.3+ for ML capabilities
- geopandas for geospatial operations
- statsmodels for statistical analysis

### Database Schema
Tables:
- `listings_sale_static` - Deduplicated sale listings
- `listings_rent_static` - Deduplicated rent listings

Views:
- `mart_city_month_sale` - Monthly sale aggregations
- `mart_city_month_rent` - Monthly rent aggregations
- `mart_city_month_yield_proxy` - Monthly yield calculations

### Features Highlights
- 21,991+ sale listings analyzed
- 8 months of historical data (Aug 2023 - Jun 2024)
- 18 districts coverage in Warsaw
- 30+ data attributes per listing
- Real-time filtering with instant chart updates
- Responsive UI with custom CSS styling
- Card-based layout with gradients
- Sidebar filters with gray card sections
- Trend indicators (↑/↓) on all KPIs

## [Unreleased]

### Planned
- Advanced statistical models (regression, clustering)
- Map visualizations with geospatial layers
- Export functionality (CSV, Excel, PDF reports)
- Data quality dashboard
- Automated data refresh pipeline
- API for external integrations
- Mobile-responsive improvements

---

## Version History

- **0.1.0** (2026-01-06) - Initial release with full dashboard functionality
