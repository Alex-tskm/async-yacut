from flask import jsonify


# Исключение для ошибок API
class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# Формирует JSON-ответ с ошибкой API
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# Обработчик ошибки 404
def not_found(error):
    return jsonify({'message': 'Ресурс не найден'}), 404


# Обработчик ошибки 500
def internal_error(error):
    return jsonify({'message': 'Внутренняя ошибка сервера'}), 500
