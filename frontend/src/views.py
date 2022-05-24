import aiofiles.os
from werkzeug.exceptions import NotFound, abort
from flask import (render_template, send_from_directory, Blueprint)
from flask_login import login_required
from core.conf import BASE_DIR, UrlConf
from src.forms import SearchForm, SearchFormProduct, UploadForm
from utils.async_funcs import fetch, fetch_file
from utils.choices import Response_type
from utils.data_models import HTTPResponse
from utils.form_utils import save_form_file


analog = Blueprint('analog', __name__,
                   template_folder=BASE_DIR / 'templates',
                   static_folder=BASE_DIR / 'static')
url_conf = UrlConf()


@analog.route('/', methods=['GET', 'POST'])
async def index():
    template_name = 'index.html'
    form = SearchForm()
    if form.validate_on_submit():
        url = url_conf.search_analog_url
        query = {'query': form.search.data,
                 'search_type': form.search_type.data}
        response: HTTPResponse = await fetch(url, query)
        if response.status == 404:
            return render_template(template_name, form=form, not_found=True)
        return render_template(template_name, form=form, result=response.body)
    return render_template(template_name, form=form)


@analog.route('/search_product', methods=['GET', 'POST'])
async def search_product():
    form = SearchFormProduct()
    if form.validate_on_submit():
        url = url_conf.search_product_url
        query = {'query': form.search.data,
                 'search_type': form.search_type.data,
                 'maker': form.maker.data}
        response: HTTPResponse = await fetch(url, query)
        if response.status == 404:
            return render_template('search_product.html', form=form,
                                   not_found=True)
        return render_template('search_product.html', form=form,
                               result=response.body)
    return render_template('search_product.html', form=form)


@analog.route('/upload_xlsx', methods=['GET', 'POST'])
@login_required
async def upload_xlsx():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = url_conf.upload_analogs_url
        response = await fetch_file(url, file_path, file_name, 'xlsx_file')
        await aiofiles.os.remove(file_path)
        return {'response': response.status, 'detail': response.body}
    return render_template('upload_xlsx.html', form=form)


@analog.route('/upload_zip', methods=['GET', 'POST'])
@login_required
async def upload_zip():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = url_conf.upload_makers_url
        response = await fetch_file(url, file_path, file_name, 'zip_file')
        await aiofiles.os.remove(file_path)
        return render_template(
            'upload_zip.html', form=form, result=response.body)
    return render_template('upload_zip.html', form=form)


@analog.route('/search_analogs_list', methods=['GET', 'POST'])
async def search_analogs_list():
    form = UploadForm()
    if form.validate_on_submit():
        file_path, file_name = save_form_file(form)
        url = url_conf.search_list_analogs_url
        response_file = await fetch_file(
            url, file_path, file_name, 'xlsx_file', Response_type.Xlsx)
        await aiofiles.os.remove(file_path)
        return render_template(
            'search_analog_list.html', form=form, resonse_file=response_file)
    return render_template('search_analog_list.html', form=form)


@analog.route('/get_file/<string:file_name>', methods=['GET'])
def get_file(file_name: str):
    try:
        return send_from_directory(
            BASE_DIR.joinpath('static'), file_name, as_attachment=True)
    except NotFound:
        abort(404)
