from setuptools import setup, find_packages

setup(
    name="inventory_module",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psycopg2-binary",
        "python-dotenv",
        "alembic"
    ],
    python_requires=">=3.8",
    test_suite="tests",
    entry_points={
        "console_scripts": [
            "inventory-cli=inventory.cli:main"
        ]
    }
    
)
