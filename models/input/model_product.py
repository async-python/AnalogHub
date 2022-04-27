from typing import Optional

from models.input.base_model import OrjsonBase
from services.transliterate import delete_symbols


class DataProductEntry(OrjsonBase):

    def __init__(self, *args, **kwargs):
        kwargs['name_ngram'] = delete_symbols(kwargs['name'])
        kwargs['name_string'] = kwargs['name_ngram']
        super().__init__(*args, **kwargs)

    article: Optional[str] = None
    name_string: str
    name_ngram: str
    name: str
    maker: str
    search_field: Optional[str] = None  # если обозначение в прайсе не явное
    description: Optional[str] = None
    position_state: Optional[str] = None
    product_line: Optional[str] = None
