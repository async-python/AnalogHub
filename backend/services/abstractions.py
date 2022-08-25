from abc import ABC, abstractmethod


class QueryServiceAbs(ABC):

    @abstractmethod
    def get_multimatch_query(self) -> dict:
        pass


class DataBaseServiceAbs(ABC):

    @abstractmethod
    def get_list_by_query(self, query: dict):
        pass

    @abstractmethod
    def get_obj_by_id(self, obj_id: str):
        pass


class AnalogServiceAbs(ABC):

    def __init__(self, query_service, db_service):
        self.query_service = query_service
        self.db_service = db_service

    @abstractmethod
    def search_list_analogs(self):
        pass

    @abstractmethod
    def search_analogs_ngram(self):
        pass

    @abstractmethod
    def search_analogs_string(self):
        pass

    @abstractmethod
    def search_products_ngram(self):
        pass

    @abstractmethod
    def search_products_string(self):
        pass
