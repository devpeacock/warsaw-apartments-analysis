#!/usr/bin/env python
"""
Verification script to check if the environment is set up correctly.
Run this after installing dependencies to ensure everything works.
"""
import sys
from pathlib import Path


def check_imports():
    """Check if all required packages can be imported."""
    print("Checking package imports...")
    required = [
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "plotly",
        "sklearn",
        "duckdb",
        "streamlit",
        "geopandas",
        "statsmodels",
        "patsy",
    ]
    
    failed = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT FOUND")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required packages found!")
    return True


def check_custom_package():
    """Check if the apartments package is installed."""
    print("\nChecking custom package...")
    try:
        import apartments
        print("  ✓ apartments package")
        
        # Check submodules
        from apartments import cleaning, viz, labels, location
        print("  ✓ apartments submodules")
        print("\n✅ Custom package installed correctly!")
        return True
    except ImportError as e:
        print(f"  ✗ apartments package - NOT FOUND")
        print(f"  Error: {e}")
        print("\nRun: pip install -e .")
        return False


def check_data_structure():
    """Check if the data directory structure exists."""
    print("\nChecking data directory structure...")
    
    required_dirs = [
        "data",
        "data/raw",
        "data/raw/sale",
        "data/raw/rent",
        "data/processed",
        "data/reference",
    ]
    
    missing = []
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ - NOT FOUND")
            missing.append(dir_path)
    
    if missing:
        print(f"\n⚠️  Missing directories: {', '.join(missing)}")
        print("Create them or ensure you're in the project root.")
        return False
    
    print("\n✅ Data directory structure OK!")
    return True


def check_database():
    """Check if the database file exists."""
    print("\nChecking database...")
    
    db_path = Path("data/processed/apartments.duckdb")
    if db_path.exists():
        print(f"  ✓ {db_path}")
        
        # Try to connect
        try:
            import duckdb
            con = duckdb.connect(str(db_path), read_only=True)
            tables = con.execute("SHOW TABLES").fetchall()
            print(f"  ✓ Database accessible ({len(tables)} tables)")
            con.close()
            print("\n✅ Database OK!")
            return True
        except Exception as e:
            print(f"  ✗ Cannot connect to database: {e}")
            return False
    else:
        print(f"  ✗ {db_path} - NOT FOUND")
        print("\n⚠️  Database not found. Run: python scripts/build_db.py")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("APARTMENTS PROJECT - ENVIRONMENT VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        check_imports(),
        check_custom_package(),
        check_data_structure(),
        check_database(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Environment is ready!")
        print("\nYou can now run:")
        print("  streamlit run streamlit_app/app.py")
    else:
        print("❌ SOME CHECKS FAILED - See above for details")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
