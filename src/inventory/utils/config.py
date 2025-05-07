import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', 5432)
    DB_NAME = os.getenv('DB_NAME', 'inventory_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

    @classmethod
    def validate(cls):
        required = ['DB_HOST', 'DB_USER', 'DB_NAME']
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise EnvironmentError(f"Variables faltantes: {', '.join(missing)}")


Config.validate()