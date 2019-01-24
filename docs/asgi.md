### So ...
notes:
`ASGI` is not yet an official specification.

It was designed by the `Django team (Andrew Godwin)`.
It has to go throw the `PEP` process yet.

But many projects has accepted it and started to support it.

- `Daphne, uvicorn, hypercorn` some ASGI servers.
- `channels, starlette, quart` some ASGI frameworks.

`Werkzeug/Flask1`, `Falcon`, `Sanic` and `Django` itslef teams are considerating
briging ASGI support to the frameworks.


---

## Let's build an `ASGI` web framework


+++

```python
from thord import API

app = API()

@app.route('/hello/{name}')
def hello(req, name: str) -> dict:
    return {'hello': name}


def create_user(name: req.Form, email: req.Form) -> dict:
    idx = User.create(name=name, email=email)
    return {'id': idx}

app.add_route('/user/', methods=['post'])

if __name__ == '__main__':
    app.run()
```