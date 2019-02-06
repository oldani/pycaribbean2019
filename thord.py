from http import HTTPStatus
from json import dumps
from typing import Any, Union, Callable
from urllib.parse import parse_qs
from wsgiref.headers import Headers as _Headers


class Headers(_Headers):
    def items(self):
        return [(k.encode(), v.encode()) for k, v in self._headers]


class QueryArgs(dict):
    def __init__(self, query_string: str) -> None:
        """ Parse qs an pass to dict class. """
        super().__init__(parse_qs(query_string))

    def get(self, key: str, default=None) -> Any:
        """ Return first value for a given key. """
        try:
            return self[key][0]
        except KeyError:
            return default

    def get_list(self, key: str, default=[]) -> list:
        """ For a given key return a list with all the values
            associated with it. """
        try:
            return self[key]
        except KeyError:
            return default


class Request:
    def __init__(self, scope, receive):
        self._scope = scope
        query_string = scope["query_string"].decode()
        self.args = QueryArgs(query_string)


class Response:
    media_type = "application/json"
    charset = "utf-8"

    def __init__(self, content: Union[dict, list, tuple], status_code: int = 200):
        """ Setup response object, initialize headers. """
        self.status_code = HTTPStatus(status_code)
        try:
            self.content = dumps(content).encode()
        except TypeError:
            raise ValueError("Response content must be JSON serializable")

        self.headers = Headers()
        self.headers.add_header(
            "content-type", f"{self.media_type}; charset={self.charset}"
        )
        self.headers.add_header("content-length", str(len(self.content)))

    async def __call__(self, send):
        """ Initialize and send response. """
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.headers.items(),
            }
        )

        await send({"type": "http.response.body", "body": self.content})


class API:
    def __call__(self, scope) -> Callable:
        """ Checkout scope, save it and return a handler coroutine. """
        assert scope["type"] == "http"
        self.scope = scope
        return self.handle_request

    async def handle_request(self, receive, send) -> None:
        req = Request(self.scope, receive)
        response = self._view(req)
        response = Response(response)
        await response(send)

    def add_view(self, view):
        """ Takes in view and save it. """
        self._view = view
