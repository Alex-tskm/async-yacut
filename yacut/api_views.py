from flask import jsonify, request

from . import app, db
from .models import URLMap
from .utils import get_unique_short_id, validate_custom_id
from .error_handlers import InvalidAPIUsage


# Создание короткой ссылки через API
@app.route('/api/id/', methods=['POST'])
def create_short():
    data = request.get_json(force=True, silent=True)

    # Проверяем наличие тела запроса
    if data is None or len(data) == 0:
        raise InvalidAPIUsage('Отсутствует тело запроса', 400)

    # Проверяем обязательное поле url
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!', 400)

    original_url = data['url']
    custom_id = data.get('custom_id')

    short_id = None
    if custom_id is not None and custom_id != '':
        ok, message = validate_custom_id(custom_id)
        if not ok:
            raise InvalidAPIUsage(message, 400)

        # Зарезервированные имена считаются занятыми
        reserved = {'files'}
        if custom_id in reserved:
            raise InvalidAPIUsage(
                "Предложенный вариант короткой ссылки уже существует.",
                400)

        # Проверяем, не занят ли custom_id в базе
        existing = URLMap.query.filter_by(short=custom_id).first()
        if existing:
            raise InvalidAPIUsage(
                "Предложенный вариант короткой ссылки уже существует.",
                400)
        short_id = custom_id
    else:
        # Генерируем случайный short_id
        short_id = get_unique_short_id()

    urlmap = URLMap(original=original_url, short=short_id)
    db.session.add(urlmap)
    db.session.commit()

    base_url = request.host_url.rstrip('/')
    return jsonify({
        'url': urlmap.original,
        'short_link': f'{base_url}/{urlmap.short}'
    }), 201


# Получение оригинальной ссылки по short_id
@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url(short_id):
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if urlmap is None:
        raise InvalidAPIUsage("Указанный id не найден", 404)
    return jsonify({'url': urlmap.original}), 200
