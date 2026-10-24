import aiohttp
from flask import (
    current_app,
    render_template,
    request,
    redirect,
    flash,
)
from werkzeug.utils import secure_filename

from . import app, db
from .models import URLMap
from .forms import ShortenLinkForm, FilesUploadForm
from .utils import get_unique_short_id, validate_custom_id


# Загружает файл на Яндекс Диск и возвращает ссылку для скачивания
async def upload_file_to_yandex(session, file, path_on_disk):
    token = current_app.config.get('DISK_TOKEN')
    host = current_app.config.get('API_HOST', 'https://cloud-api.yandex.net')
    version = current_app.config.get('API_VERSION', 'v1')
    base_url = f"{host}/{version}"

    if not token:
        raise RuntimeError("DISK_TOKEN не задан в переменных окружения (.env)")

    # Получаем URL для загрузки файла
    async with session.get(
        f"{base_url}/disk/resources/upload",
        headers={"Authorization": f"OAuth {token}"},
        params={"path": path_on_disk}
    ) as resp:
        resp.raise_for_status()
        data = await resp.json()
        upload_url = data["href"]

    # Загружаем файл
    file.seek(0)
    async with session.put(upload_url, data=file.read()) as resp:
        resp.raise_for_status()

    # Получаем ссылку для скачивания
    async with session.get(
        f"{base_url}/disk/resources/download",
        headers={"Authorization": f"OAuth {token}"},
        params={"path": path_on_disk}
    ) as resp:
        resp.raise_for_status()
        d_data = await resp.json()
        return d_data["href"]


# Главная страница: форма сокращения ссылки
@app.route('/', methods=['GET', 'POST'])
def index():
    form = ShortenLinkForm()
    result_short = None
    result_link = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = (
            form.custom_id.data.strip() if form.custom_id.data else None
        )

        short_id = None
        if custom_id:
            ok, message = validate_custom_id(custom_id)
            if not ok:
                flash(message, 'error')
                return render_template(
                    'index.html', form=form,
                    result_short=result_short)

            # Зарезервированные имена считаются занятыми
            reserved = {'files'}
            if custom_id in reserved:
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'error')
                return render_template(
                    'index.html', form=form,
                    result_short=result_short)

            # Проверяем дубликат в базе
            existing = URLMap.query.filter_by(short=custom_id).first()
            if existing:
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'error')
                return render_template(
                    'index.html', form=form,
                    result_short=result_short)
            short_id = custom_id
        else:
            short_id = get_unique_short_id()

        urlmap = URLMap(original=original, short=short_id)
        db.session.add(urlmap)
        db.session.commit()

        # Формируем полную ссылку для отображения
        base_url = request.host_url.rstrip('/')
        result_short = short_id
        result_link = f"{base_url}/{short_id}"

        flash(f'Короткая ссылка: {short_id}', 'success')

        # Очищаем форму, чтобы не отправлять повторно
        form = ShortenLinkForm(formdata=None)
        return render_template(
            'index.html',
            form=form,
            result_short=result_short,
            result_link=result_link
        )

    return render_template(
        'index.html', form=form,
        result_short=result_short)


# Страница загрузки файлов
@app.route('/files', methods=['GET', 'POST'])
async def files_upload():
    form = FilesUploadForm()
    results = []
    base_url = request.host_url.rstrip('/')

    if form.validate_on_submit():
        files = request.files.getlist('files')
        if not files or all(not f.filename for f in files):
            flash('Выберите хотя бы один файл для загрузки.', 'error')
            return render_template(
                'files.html', form=form,
                results=results, base_url=base_url)

        async with aiohttp.ClientSession() as session:
            for file in files:
                if not file.filename:
                    continue

                original_filename = file.filename

                filename = secure_filename(file.filename)
                short_id = get_unique_short_id()
                path_on_disk = f"/ya-cut-files/{filename}"

                try:
                    download_url = await upload_file_to_yandex(
                        session, file, path_on_disk)
                except Exception as e:
                    flash(
                        f"Ошибка загрузки файла {original_filename}: {e}",
                        'error')
                    continue

                urlmap = URLMap(original=download_url, short=short_id)
                db.session.add(urlmap)

                results.append((original_filename, short_id))

        db.session.commit()

    return render_template(
        'files.html', form=form,
        results=results, base_url=base_url)


# Перенаправление по короткой ссылке
@app.route('/<short_id>')
def redirect_or_download(short_id):
    urlmap = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(urlmap.original)
