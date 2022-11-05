from models.base_model import OrjsonBase


class Message404(OrjsonBase):
    detail: str = 'Item not found'
