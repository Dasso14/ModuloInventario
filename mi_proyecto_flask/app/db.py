# app/db.py
from flask_sqlalchemy import SQLAlchemy

# Inicializa la extensión SQLAlchemy.
# Esta instancia 'db' se importará en la fábrica de la aplicación y en los modelos.
db = SQLAlchemy()
