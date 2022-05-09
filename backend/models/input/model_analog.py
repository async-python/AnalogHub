from typing import Optional

from models.input.base_model import OrjsonBase
from services.transliterate import delete_symbols


class DataAnalogEntry(OrjsonBase):

    def __init__(self, *args, **kwargs):
        kwargs['base_name_ngram'] = delete_symbols(kwargs['base_name'])
        kwargs['analog_name_ngram'] = delete_symbols(kwargs['analog_name'])
        kwargs['base_name_string'] = kwargs['base_name_ngram']
        kwargs['analog_name_string'] = kwargs['analog_name_ngram']
        super().__init__(*args, **kwargs)

    base_name_string: Optional[str] = None
    base_name_ngram: Optional[str] = None
    base_name: Optional[str] = None
    base_maker: Optional[str] = None
    analog_name_string: Optional[str] = None
    analog_name_ngram: Optional[str] = None
    analog_name: Optional[str] = None
    analog_maker: Optional[str] = None
