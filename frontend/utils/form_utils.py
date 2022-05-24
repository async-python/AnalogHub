from werkzeug.datastructures import FileStorage

from core.conf import BASE_DIR
from src.forms import UploadForm


def save_form_file(form: UploadForm):
    file: FileStorage = form.file.data
    file_name = file.filename
    file_path = str(BASE_DIR / f'static/{file_name}')
    file.save(file_path)
    return file_path, file_name
