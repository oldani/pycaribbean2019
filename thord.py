import re
import inspect
from functools import lru_cache
from http import HTTPStatus
from json import dumps
from typing import Any, Union, Callable
from urllib.parse import parse_qs, urlparse
from wsgiref.headers import Headers as _Headers


class NotFound(Exception):
    pass


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


class URL:
    def __init__(self, scope) -> None:
        path: str = f"{scope['root_path']}{scope['path']}"
        self._url: str = (
            f"{scope['scheme']}://{scope['server'][0]}:{scope['server'][1]}"
            f"{path}?{scope['query_string'].decode()}"
        )
        self.url = urlparse(self._url)

    def __repr__(self) -> str:
        return f"URL({self._url})"

    def __eq__(self, value) -> bool:
        return self._url == str(value)

    def __getattr__(self, name: str) -> str:
        return getattr(self.url, name)


class Request:
    def __init__(self, scope, receive):
        self._scope = scope
        query_string = scope["query_string"].decode()
        self.args: QueryArgs = QueryArgs(query_string)
        self.url: URL = URL(scope)


class Route:
    _pattern = re.compile("{([^{}]*)}")

    def __init__(self, route: str) -> None:
        self.route = route
        self.setup_route()

    def __eq__(self, other):
        if isinstance(other, self):
            return self.route == other.route
        else:
            return self.match(other)

    def __hash__(self):
        return hash(self._regex)

    def setup_route(self):
        """ Create a regex for matching incoming routes.
            _pattern is a rx for matching {fields} in views patterns.
            _pattner.sub calls Route.replace_field in each match
            and replace it for group capturing rx. 
            /test/{id} will be compile to ^/test/(?P<id>[^/]+?)$   """
        self._regex = re.compile(
            f"^{self._pattern.sub(self.replace_field, self.route)}$"
        )

    @staticmethod
    def replace_field(match):
        return f"(?P<{match.group(1)}>[^/]+?)"

    def match(self, _str: str):
        """ March a path with this routes.
            @return:
                - dict {field: value} for routes with fields.
                - True if matched but no field
                - None for no matches. """
        result = self._regex.match(_str)
        if result:
            return result.groupdict() or True


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
    def __init__(self) -> None:
        self._routes: dict = {}

    def __call__(self, scope) -> Callable:
        """ Checkout scope, save it and return a handler coroutine. """
        assert scope["type"] == "http"
        self.scope = scope
        return self.handle_request

    async def handle_request(self, receive, send) -> None:
        req = Request(self.scope, receive)
        try:
            response = await self.dispatch(req)
        except NotFound:
            response = Response("Not found", status_code=404)
        await response(send)

    def add_route(self, pattern: str, view: Callable) -> None:
        """ Convert pattern to a Route obj, save it internally
            and assign view. """
        route = Route(pattern)
        self._routes[route] = view

    def route(self, pattern: str) -> Callable:
        """ Takes in view and save it. """

        def warpper(view: Callable) -> Callable:
            self.add_route(pattern, view)
            return view

        return warpper

    @lru_cache(maxsize=256)  # If we already saw this path cache it
    def get_view(self, path):
        """ Retrieve view for a given path. """
        _view, params = None, {}
        for route, view in self._routes.items():
            match = route.match(path)
            if not match:
                continue
            if match and isinstance(match, dict):  # Means route have parameters
                _view, params = view, match
            else:
                _view = view
        return _view, params

    async def dispatch(self, req):
        """ Execute view for a given request. """
        view, params = self.get_view(req.url.path)
        if not view:
            raise NotFound()
        if inspect.iscoroutinefunction(view):
            respose = await view(req, **params)
        else:
            respose = view(req, **params)
        return Response(respose)
