import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from .utils.config import Config

class Database:
    _connection_pool = None

    @classmethod
    def initialize(cls):
        cls._connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=Config.DB_POOL_MIN,
            maxconn=Config.DB_POOL_MAX,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )

    @classmethod
    @contextmanager
    def get_cursor(cls):
        conn = cls._connection_pool.getconn()
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
    def close_all(cls):
        cls._connection_pool.closeall()
