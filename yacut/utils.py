import random
import string
from yacut.models import URLMap

# Допустимые символы для генерации short_id
ALLOWED_CHARS = string.ascii_letters + string.digits


# Генерирует уникальный short_id заданной длины
def get_unique_short_id(length=6, max_attempts=10):
    for _ in range(max_attempts):
        candidate = ''.join(random.choices(ALLOWED_CHARS, k=length))
        if not URLMap.query.filter_by(short=candidate).first():
            return candidate
    raise RuntimeError("Не удалось сгенерировать уникальный short ID")


# Проверяет валидность custom_id: длина и символы
def validate_custom_id(custom_id):
    if len(custom_id) > 16:
        return False, "Указано недопустимое имя для короткой ссылки"

    if not custom_id.isascii() or not custom_id.isalnum():
        return False, "Указано недопустимое имя для короткой ссылки"

    return True, ""
