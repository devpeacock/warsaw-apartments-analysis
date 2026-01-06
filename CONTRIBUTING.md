# Contributing Guide

## Struktura kodu

### Pakiet `apartments` (src/apartments/)

Główny pakiet Python z modułami analitycznymi:

- **cleaning.py** - Czyszczenie i walidacja danych
- **fingerprint.py** - Tworzenie unikalnych identyfikatorów nieruchomości
- **io.py** - Ładowanie danych z CSV i bazy danych
- **labels.py** - Mapowania nazw kolumn i wartości dla UI
- **location.py** - Geokodowanie i przypisywanie dzielnic
- **rental_yield.py** - Kalkulacje rentowności wynajmu
- **viz.py** - Funkcje wizualizacji Plotly

### Dashboard Streamlit (streamlit_app/)

Struktura aplikacji wielostronicowej:

```
streamlit_app/
├── app.py              # Strona główna
├── components/
│   ├── loaders.py     # Ładowanie danych z DuckDB
│   ├── sidebar.py     # Filtry w sidebarze
│   └── ui.py          # Komponenty UI i CSS
└── pages/
    ├── 1_Sale.py      # Analiza sprzedaży
    ├── 2_Rent.py      # Analiza wynajmu
    ├── 3_Yield.py     # Analiza rentowności
    └── 4_Time_Series.py # Trendy czasowe
```

## Workflow deweloperski

### 1. Dodawanie nowej funkcji do pakietu

```python
# src/apartments/new_feature.py

def new_analysis_function(df):
    """
    Opis funkcji.
    
    Args:
        df: DataFrame z danymi
    
    Returns:
        DataFrame z wynikami
    """
    # Implementacja
    return result
```

Dodaj importy do `__init__.py`:
```python
# src/apartments/__init__.py
from .new_feature import new_analysis_function
```

### 2. Dodawanie nowej strony do dashboardu

```python
# streamlit_app/pages/5_New_Page.py
import streamlit as st
from components.ui import inject_global_css, header

inject_global_css()
header("Tytuł", "Opis")

# Twoja analiza
```

### 3. Modyfikowanie SQL views

Edytuj `scripts/build_db.py`:
```python
con.execute("""
    CREATE VIEW my_new_view AS
    SELECT ...
    FROM ...
""")
```

Następnie przebuduj bazę:
```bash
python scripts/build_db.py
```

## Testowanie

### Uruchom istniejące testy

```bash
pytest tests/
```

### Dodaj nowy test

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

## Konwencje kodu

### Style

- **Black** formatter dla formatowania
- **Type hints** dla nowych funkcji
- **Docstrings** w stylu Google

```python
def example_function(df: pd.DataFrame, col: str) -> float:
    """
    Krótki opis funkcji.
    
    Args:
        df: DataFrame z danymi
        col: Nazwa kolumny do analizy
    
    Returns:
        Wynik jako float
    
    Raises:
        ValueError: Jeśli kolumna nie istnieje
    """
    if col not in df.columns:
        raise ValueError(f"Column {col} not found")
    return df[col].mean()
```

### Nazewnictwo

- **Funkcje**: `snake_case`
- **Klasy**: `PascalCase`
- **Stałe**: `UPPER_CASE`
- **Pliki**: `snake_case.py`

### Imports

Grupuj importy w kolejności:
1. Biblioteki standardowe
2. Biblioteki zewnętrzne
3. Lokalne moduły

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

## Debugowanie

### Streamlit

Dodaj debugging print:
```python
st.write("Debug:", variable)
st.dataframe(df.head())
```

### DuckDB queries

Test queries w Python:
```python
import duckdb
con = duckdb.connect('data/processed/apartments.duckdb')
result = con.execute("SELECT * FROM view_name LIMIT 5").fetchdf()
print(result)
```

## Performance

### Caching w Streamlit

Użyj `@st.cache_data` dla funkcji ładujących dane:
```python
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")
```

### Optymalizacja SQL

- Używaj widoków dla powtarzalnych zapytań
- Indeksuj kolumny używane w JOIN
- Agreguj w SQL, nie w Pandas

## Commit messages

Format: `type: description`

Types:
- `feat:` - nowa funkcjonalność
- `fix:` - naprawa błędu
- `docs:` - dokumentacja
- `style:` - formatowanie kodu
- `refactor:` - refaktoryzacja
- `test:` - testy
- `chore:` - maintanance

Przykłady:
```
feat: add district comparison chart to Sale page
fix: handle missing values in price_per_m2 calculation
docs: update README with new setup instructions
```

## Troubleshooting

### Problem: Streamlit nie widzi zmian w pakiecie

```bash
pip install -e . --force-reinstall --no-deps
```

### Problem: DuckDB locked

Zamknij wszystkie połączenia:
```python
con.close()
```

### Problem: Plotly chart nie wyświetla się

Sprawdź czy używasz `st.plotly_chart()`:
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
