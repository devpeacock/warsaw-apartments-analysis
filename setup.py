from setuptools import setup, find_packages

# Find packages in src/ (apartments module)
src_packages = find_packages(where="src")

# Find packages in streamlit_app/ (streamlit components)
streamlit_packages = find_packages(where="streamlit_app")
streamlit_packages = ["streamlit_app." + p for p in streamlit_packages] + ["streamlit_app"]

setup(
    name="apartments",
    version="0.1.0",
    description="Warsaw apartments price analysis",
    author="",
    packages=src_packages + streamlit_packages,
    package_dir={"": "src", "streamlit_app": "streamlit_app"},
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
        "psycopg2",
        "streamlit>=1.30",
        "plotly>=5.17",
        "geopandas",
        "patsy",
        "statsmodels",
    ],
)
