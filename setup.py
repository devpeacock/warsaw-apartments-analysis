from setuptools import setup, find_packages

setup(
    name="apartments",
    version="0.1.0",
    description="Warsaw apartments price analysis",
    author="",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.0",
        "numpy>=1.24",
        "matplotlib",
        "seaborn",
        "scikit-learn>=1.3",
        "scipy",
        "duckdb",
        "sqlalchemy",
        "psycopg2-binary",
        "streamlit>=1.30",
        "plotly>=5.17",
        "geopandas",
        "patsy",
        "statsmodels",
    ],
)
