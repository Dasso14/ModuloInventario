import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from inventory.utils.config import Config

class Database:
    connection_pool = None

    @classmethod
    def initialize(cls):
        cls._connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=Config.DB_POOL_MIN,
            maxconn=Config.DB_POOL_MAX * 2,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )

    @classmethod
    @contextmanager
    def get_cursor(cls):
        conn = cls.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cls._connection_pool.putconn(conn)

    @classmethod
    def get_connection(cls):
        if not cls.connection_pool:
            cls.initialize()
        return cls.connection_pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        cls.connection_pool.putconn(conn)

    @classmethod
    def close_all(cls):
        cls._connection_pool.closeall()

    @classmethod
    def monitor_pool(cls):
        return {
            "connections_used": cls.connection_pool._used,
            "connections_free": cls.connection_pool._rused
        }

class DatabaseError(Exception):
    """Excepción base para errores de base de datos"""

class ConnectionFail(DatabaseError):
    """Falló la conexión a la DB"""

class QueryExecutionError(DatabaseError):
    """Error en ejecución de query"""