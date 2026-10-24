from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# Создаём экземпляр Flask-приложения и загружаем конфигурацию
app = Flask(__name__)
app.config.from_object(Config)

# Инициализируем базу данных и миграции
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Регистрируем модули с маршрутами
from . import views, api_views, error_handlers  # noqa


# Регистрируем обработчики ошибок
from .error_handlers import (
    not_found,
    internal_error,
    InvalidAPIUsage,
    handle_invalid_usage,
)

app.register_error_handler(404, not_found)
app.register_error_handler(500, internal_error)


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return handle_invalid_usage(error)
