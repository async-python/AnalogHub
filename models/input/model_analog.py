from typing import Optional

from models.base_model import OrjsonBase
from services.transliterate import delete_symbols


class DataAnalogEntry(OrjsonBase):

    def __init__(self, *args, **kwargs):
        base_name = kwargs['base_name']
        analog_name = kwargs['analog_name']
        kwargs['base_name_clean'] = delete_symbols(base_name)
        kwargs['analog_name_clean'] = delete_symbols(analog_name)
        super().__init__(*args, **kwargs)

    base_name_clean: Optional[str] = None
    base_name: Optional[str] = None
    base_maker: Optional[str] = None
    analog_name_clean: Optional[str] = None
    analog_name: Optional[str] = None
    analog_maker: Optional[str] = None
