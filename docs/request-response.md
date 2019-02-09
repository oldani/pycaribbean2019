### Request / Response abstractions


+++

### `We want something like this`

```python
def application(scope):
    assert scope["type"] == "http"

    async def asgi(receive, send):
        req = Request(scope, receive)
        name = req.args.get("name")
        response = Response(f"Hello {name}!")
        await response(send)

    return asgi
```
notes:


+++

### So ...
#### How does or Request and Response objects looks like? <!-- .element: class="fragment" -->

+++


#### For the Request object we got this:

```python
from urllib.parse import parse_qs
...
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
        ...
class Request:
    def __init__(self, scope, receive):
        self._scope = scope
        query_string = scope["query_string"].decode()
        self.args = QueryArgs(query_string)
```
<!-- .element: class="stretch stretch-plus" -->


+++

#### And for the Response object:

```python
from http import HTTPStatus
from json import dumps
from wsgiref.headers import Headers as _Headers

class Headers(_Headers):
    def items(self):
        return [(k.encode(), v.encode())
                for k, v in self._headers]
...
```


+++

#### And

```python
...
class Response:
    media_type = "application/json"
    charset = "utf-8"

    def __init__(self, content: Union[dict, list, tuple],
      status_code: int = 200):
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
...
```
<!-- .element: class="stretch stretch-plus wider" -->


+++

#### Plus

```python
...
   async def __call__(self, send):
        """ Initialize and send response. """
        await send({
          "type": "http.response.start",
          "status": self.status_code,
          "headers": self.headers.items(),
        })
        await send(
          {"type": "http.response.body", "body": self.content})
```


---

### `Yet this looks even better`


```python
from thord import API

app = API()

@app.add_view
def hello(req):
    return f"Hello {req.args.get('name')}!"
```

```shell
$ uvicorn api:app
```
<!-- .element: class="fragment" -->


+++

### Then <!-- .element: class="fragment" -->
#### `How do we get there?` <!-- .element: class="fragment" -->

```python
class API:
    def __call__(self, scope) -> Callable:
        """ Checkout scope, save it and return a handler
            coroutine. """
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
```
<!-- .element: class="fragment" -->
notes:

- Replace the func by a class
- Make it a callable
- return a coroutine
- Create a decorator to save our view
