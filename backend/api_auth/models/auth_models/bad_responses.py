from models.base_model import OrjsonBase


class Model400(OrjsonBase):
    message: str = 'Bad request'


class Model401(OrjsonBase):
    message: str = 'Not authorized'
