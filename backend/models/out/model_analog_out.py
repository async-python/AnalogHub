from typing import Optional

from models.out.base_model_out import OrjsonBaseOut


class DataAnalogOut(OrjsonBaseOut):
    base_name: Optional[str] = None
    base_maker: Optional[str] = None
    analog_name: Optional[str] = None
    analog_maker: Optional[str] = None
