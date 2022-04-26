import re
from typing import Optional

from models.base_model import OrjsonBase
from services.transliterate import delete_symbols


class DataProductEntry(OrjsonBase):

    def __init__(self, *args, **kwargs):
        kwargs['name_clean'] = delete_symbols(kwargs['name'])
        kwargs['name_string'] = delete_symbols(kwargs['name'])
        super().__init__(*args, **kwargs)

    article: Optional[str] = None
    name_string: str
    name_clean: str
    name: str
    maker: str
    search_field: Optional[str] = None  # если обозначение в прайсе не явное
    description: Optional[str] = None
    position_state: Optional[str] = None
    product_line: Optional[str] = None
