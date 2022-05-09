from typing import Optional

from models.out.base_model_out import OrjsonBaseOut


class DataProductOut(OrjsonBaseOut):
    article: Optional[str] = None
    name: str
    maker: str
    search_field: Optional[str] = None  # если обозначение в прайсе не явное
    description: Optional[str] = None
    position_state: Optional[str] = None
    product_line: Optional[str] = None
