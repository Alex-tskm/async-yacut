from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms.validators import DataRequired, Length, Optional


# Форма для сокращения ссылки
class ShortenLinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка', validators=[DataRequired()])
    custom_id = StringField(
        'Короткий идентификатор (не обязательно)',
        validators=[Optional(), Length(max=16)])


# Форма для загрузки файлов
class FilesUploadForm(FlaskForm):
    files = FileField(
        'Файлы',
        validators=[DataRequired()],
        render_kw={'multiple': True})
