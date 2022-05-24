from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import RadioField, SearchField, SelectField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search = SearchField(label='Search', validators=[DataRequired()])
    search_type = RadioField(
        'Search type', [DataRequired()],
        choices=[('string_search', 'accurate search'),
                 ('ngram_search', 'elasticsearch')],
        default='ngram_search')
    submit = SubmitField(label='Search')


class SearchFormProduct(SearchForm):
    maker = SelectField(
        'Search type', [DataRequired()],
        choices=['ALL', 'PALBIT', 'YG-1', 'VERGNANO', 'VARGUS', 'SANHOG',
                 'OMAP', 'NANOLOY', 'LIKON', 'HORN', 'HELION',
                 'GABRIEL_MAUVAIS', 'FRESAL', 'DEREK', 'BRICE', 'Bribase',
                 'ASKUP', 'ILIX'],
        default='ALL')


class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired()])
