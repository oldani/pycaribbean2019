### So ...
notes:
`ASGI` is not yet an official specification.

It was designed by the `Django team (Andrew Godwin)`.
It has to go throw the `PEP` process yet.

But many projects has accepted it and started to support it.

- `Daphne, uvicorn, hypercorn` some ASGI servers.
- `channels, starlette, quart` some ASGI frameworks.

`Werkzeug/Flask1`, `Falcon`, `Sanic` and `Django` it self teams are considering
bringing ASGI support to the frameworks.


---

## Let's build an `ASGI` web framework


+++

```python
from thord import API

app = API()

@app.route('/hello/{name}')
def hello(req, name: str) -> dict:
    return {'hello': name}


def bye(name: str) -> dict:
    return {name: 'Game over!'}

app.add_route('/user/', methods=['post'])

if __name__ == '__main__':
    app.run()
```


---

### Hello PyCaribbean!

```python
from json import dumps

def application(scope):
    assert scope["type"] == "http"

    async def asgi(receive, send):
        response = dumps("Hello PyCarribean!")
        await send({
            "type": "http.response.start", "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        })

        await send({
            "type": "http.response.body", "body": response.encode()
        })

    return asgi
```
<!-- .element: class="stretch" -->
notes:

1. API oriented (just JSON response)
2. Since we don't have much time, just support for `http`

First the `assert`, we will be only working with `http`, we don't have much time
for websocket and other stuffs.

What is `scope - connection scope`? What it have?
- `Dict` with the connection context data, except for `request.body`
- `scope['type']` can be http, websocket or lifespan.

`send` and `recieve` are our way to listen to `events` and send data back.


+++


### `{Connection Scope}` <!-- .element: class="fragment" -->
#### How it looks like? <!-- .element: class="fragment" -->
```python
{
    "type": "http",
    "http_version": "1.1",
    "server": ("127.0.0.1", 8001),
    "client": ("127.0.0.1", 57596),
    "scheme": "http",
    "method": "GET",
    "root_path": "",
    "path": "/",
    "query_string": b"",
    "headers": [
        (b"cache-control", b"no-cache"),
        (b"user-agent", b"PostmanRuntime/6.4.1"),
        (b"accept", b"*/*"),
        (b"accept-encoding", b"gzip, deflate"),
        (b"connection", b"keep-alive"),
    ],
}
```
<!-- .element: class="fragment" -->


---


### Hello `{name}`

```python
from json import dumps
from urllib.parse import parse_qs

def application(scope):
    assert scope["type"] == "http"

    async def asgi(receive, send):
        args = parse_qs(scope["query_string"].decode())
        response = dumps(f"Hello {args.get('name')[0]}!")
        await send({
            "type": "http.response.start", "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        })

        await send({
            "type": "http.response.body", "body": response.encode()})

    return asgi
```
<!-- .element: class="stretch" -->
notes:
