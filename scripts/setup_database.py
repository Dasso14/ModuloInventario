import psycopg2
from inventory.database import Database
from inventory.utils.config import Config


def setup_database():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Crear base de datos si no existe
    cursor.execute(f"CREATE DATABASE {Config.DB_NAME}")
    
    # Ejecutar schema SQL
    with open("schema.sql") as f:
        cursor.execute(f.read())
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()