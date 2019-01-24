from json import dumps
from urllib.parse import parse_qs


def application(scope):
    assert scope["type"] == "http"

    async def asgi(receive, send):
        args = parse_qs(scope["query_string"].decode())
        response = dumps(f"Hello {args.get('name')[0]}!")
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            }
        )

        await send({"type": "http.response.body", "body": response.encode()})

    return asgi
