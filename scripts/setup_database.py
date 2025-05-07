import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from src.inventory.utils.config import Config

def setup_database():
    try:
        # 1. Conectar a PostgreSQL para crear la DB
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 2. Verificar y crear DB
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = {}")
            .format(sql.Literal(Config.DB_NAME))
        )

        if not cursor.fetchone():
            cursor.execute(
                sql.SQL("CREATE DATABASE {}")
                .format(sql.Identifier(Config.DB_NAME))
            )
            print(f"Base de datos '{Config.DB_NAME}' creada")
        else:
            print(f"La DB '{Config.DB_NAME}' ya existe")

        cursor.close()
        conn.close()

        # 3. Ejecutar schema.sql en la nueva DB
        with psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                with open("schema.sql", "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                    cursor.execute(schema_sql)
                print("Esquema SQL ejecutado")

    except psycopg2.Error as e:
        print(f"Error PostgreSQL: {e}")
    except FileNotFoundError:
        print("Error: schema.sql no encontrado")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    setup_database()