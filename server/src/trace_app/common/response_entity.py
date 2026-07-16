from typing import TypeVar, Generic

from mg_app_framework import MesCode

T = TypeVar('T')


class Response(Generic[T]):
    data: T
    code: str

    def __init__(self, code: str = MesCode.success, data: T = None, info: str = ''):
        self.data = data
        self.code = code
        self.info = info

    @staticmethod
    def fail(info: str, data: T = '') -> 'Response':
        return Response(MesCode.fail, data, info=info)

    @staticmethod
    def success(data: T = '', info: str = None) -> 'Response':
        return Response(MesCode.success, data, info=info)
