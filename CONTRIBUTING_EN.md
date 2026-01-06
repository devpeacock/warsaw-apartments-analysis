# Contributing Guide

## Code Structure

### Package `apartments` (src/apartments/)

Main Python package with analytical modules:

- **cleaning.py** - Data cleaning and validation
- **fingerprint.py** - Creating unique property identifiers
- **io.py** - Loading data from CSV and database
- **labels.py** - Column and value name mappings for UI
- **location.py** - Geocoding and district assignment
- **rental_yield.py** - Rental yield calculations
- **viz.py** - Plotly visualization functions

### Streamlit Dashboard (streamlit_app/)

Multi-page application structure:

```
streamlit_app/
├── app.py              # Home page
├── components/
│   ├── loaders.py     # Loading data from DuckDB
│   ├── sidebar.py     # Sidebar filters
│   └── ui.py          # UI components and CSS
└── pages/
    ├── 1_Sale.py      # Sale analysis
    ├── 2_Rent.py      # Rent analysis
    ├── 3_Yield.py     # Yield analysis
    └── 4_Time_Series.py # Time trends
```

## Development Workflow

### 1. Adding new feature to package

```python
# src/apartments/new_feature.py

def new_analysis_function(df):
    """
    Function description.
    
    Args:
        df: DataFrame with data
    
    Returns:
        DataFrame with results
    """
    # Implementation
    return result
```

Add imports to `__init__.py`:
```python
# src/apartments/__init__.py
from .new_feature import new_analysis_function
```

### 2. Adding new page to dashboard

```python
# streamlit_app/pages/5_New_Page.py
import streamlit as st
from components.ui import inject_global_css, header

inject_global_css()
header("Title", "Description")

# Your analysis
```

### 3. Modifying SQL views

Edit `scripts/build_db.py`:
```python
con.execute("""
    CREATE VIEW my_new_view AS
    SELECT ...
    FROM ...
""")
```

Then rebuild database:
```bash
python scripts/build_db.py
```

## Testing

### Run existing tests

```bash
pytest tests/
```

### Add new test

```python
# tests/test_new_feature.py
import pytest
from apartments.new_feature import new_analysis_function

def test_new_function():
    # Arrange
    test_data = ...
    
    # Act
    result = new_analysis_function(test_data)
    
    # Assert
    assert result is not None
```

## Code Conventions

### Style

- **Black** formatter for formatting
- **Type hints** for new functions
- **Docstrings** in Google style

```python
def example_function(df: pd.DataFrame, col: str) -> float:
    """
    Short function description.
    
    Args:
        df: DataFrame with data
        col: Column name to analyze
    
    Returns:
        Result as float
    
    Raises:
        ValueError: If column doesn't exist
    """
    if col not in df.columns:
        raise ValueError(f"Column {col} not found")
    return df[col].mean()
```

### Naming

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Files**: `snake_case.py`

### Imports

Group imports in order:
1. Standard library
2. External packages
3. Local modules

```python
# Standard library
import sys
from pathlib import Path

# External packages
import pandas as pd
import numpy as np

# Local modules
from apartments.cleaning import clean_base
from apartments.viz import plot_hist
```

## Debugging

### Streamlit

Add debugging prints:
```python
st.write("Debug:", variable)
st.dataframe(df.head())
```

### DuckDB queries

Test queries in Python:
```python
import duckdb
con = duckdb.connect('data/processed/apartments.duckdb')
result = con.execute("SELECT * FROM view_name LIMIT 5").fetchdf()
print(result)
```

## Performance

### Caching in Streamlit

Use `@st.cache_data` for data loading functions:
```python
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")
```

### SQL Optimization

- Use views for repeatable queries
- Index columns used in JOINs
- Aggregate in SQL, not in Pandas

## Commit Messages

Format: `type: description`

Types:
- `feat:` - new feature
- `fix:` - bug fix
- `docs:` - documentation
- `style:` - code formatting
- `refactor:` - refactoring
- `test:` - tests
- `chore:` - maintenance

Examples:
```
feat: add district comparison chart to Sale page
fix: handle missing values in price_per_m2 calculation
docs: update README with new setup instructions
```

## Troubleshooting

### Issue: Streamlit doesn't see package changes

```bash
pip install -e . --force-reinstall --no-deps
```

### Issue: DuckDB locked

Close all connections:
```python
con.close()
```

### Issue: Plotly chart doesn't display

Check if using `st.plotly_chart()`:
```python
import plotly.express as px
fig = px.line(df, x='date', y='price')
st.plotly_chart(fig, use_container_width=True)
```

## Resources

- [Streamlit docs](https://docs.streamlit.io/)
- [DuckDB docs](https://duckdb.org/docs/)
- [Plotly docs](https://plotly.com/python/)
- [Pandas docs](https://pandas.pydata.org/docs/)
