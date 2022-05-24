from dataclasses import dataclass

from multidict._multidict import CIMultiDictProxy


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int
