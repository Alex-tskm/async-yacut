import os


# Конфигурация приложения
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI', 'sqlite:///db.sqlite3')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
