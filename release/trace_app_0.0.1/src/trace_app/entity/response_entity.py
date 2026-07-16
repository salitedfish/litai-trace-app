from mg_app_framework import MesCode


class Response:
    """Response helper - references the real Response in common/response_entity.py"""

    @staticmethod
    def fail(info: str, data=None):
        from trace_app.common.response_entity import Response as Resp
        return Resp.fail(info, data)

    @staticmethod
    def success(data=None, info: str = None):
        from trace_app.common.response_entity import Response as Resp
        return Resp.success(data, info)
