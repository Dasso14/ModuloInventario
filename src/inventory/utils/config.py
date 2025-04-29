import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', 1))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', 10))
