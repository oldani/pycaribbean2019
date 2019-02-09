#### Async/Await

```python
import asyncio
import time

async def say_hello(time=1):
    await asyncio.sleep(time)
    print("Hello")

async def main():
    print(f"started at {time.strftime('%X')}")
    tasks = [asyncio.ensure_future(say_hello(i))
             for i in range(5)]
    for t in tasks:
        await t
    print(f"finished at {time.strftime('%X')}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

notes:
If we’re going to build an async web framework we have to know about async/await

So async/await on Python 3.6 brings a  new landscape for asynchronous programming models

Asynchronous models uses a task base switching, with explicit switch points and flow control managed within the
runtime. In contrast to thread-bases concurrency, which is more resource intensive and relies on implicit switching,
managed by the OS.

One of our challenges is how we adapt all the web frameworks that we already have to take advantage of all the
benefits that async brings to I/O programs.


+++

- Django <!-- .element: class="fragment" -->
- Flask <!-- .element: class="fragment" -->
notes:
Sadly that’s easy said than done. That’s why we have more new web frameworks (Quart, Starlette, Sanic, Channels) .


+++

- Sanic <!-- .element: class="fragment" -->
- Quart <!-- .element: class="fragment" -->
- Channels <!-- .element: class="fragment" -->


+++

### Why is this? <!-- .element: class="fragment" -->
### Why is so Hard? <!-- .element: class="fragment" -->


+++

### WSGI
#### (Web Server Gateway Interface) <!-- .element: class="fragment" -->
notes:
All the old frameworks are WSGI-based frameworks

WSGI for Web Server Gateway Interface which is a specification (not implementation)

WSGI is a standard that provides a formalized interface between the Server implementation, that deals with the
nitty-gritty details of the raw socket handling, and the Application implementation.

It provides a proper separation of concerns between these two aspects, and allows server implementations to evolve
independently of framework or application implementations.


+++

#### Why not just upgrade WSGI? <!-- .element: class="fragment" -->
```python
def hello_world(environ, start_response):
    response = b"Hello, World!\n"
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
    ])
    return [response]
```
<!-- .element: class="fragment" -->
notes:
The problem usually ends up being that WSGI’s single-callable interface just isn’t suitable for more involved Web
protocols like WebSocket.

WSGI applications are a single, synchronous callable that takes a request and returns a response; this doesn’t allow
for long-lived connections, like you get with long-poll HTTP or WebSocket connections.

Even if we made this callable asynchronous, it still only has a single path to provide a request, so protocols that
have multiple incoming events (like receiving WebSocket frames) can’t trigger this.


---

### Here is where `ASGI` comes in

```python
class Application:

    def __init__(self, scope):
        self.scope = scope

    async def __call__(self, receive, send):
        request = Request(self.scope, receive)
        ...
        await send({"type": "http.response.start", ...})
        await send({"type": "http.response.body", ...})
```
<!-- .element: class="fragment" -->

```shell
$ uvicorn thord:Application
```
<!-- .element: class="fragment" -->

notes:
The ASGI specification is an iterative but fundamental redesign, that provides an async server/application interface 
with support for HTTP, HTTP/2, and WebSockets.

ASGI is structured as a double-callable - the first callable takes a `scope`, which contains details about the incoming request, and returns a second, coroutine callable. This second callable gets given `send` and `receive` awaitables that allow the coroutine to monitor incoming events and send outgoing events.

This not only allows multiple incoming events and outgoing events for each application, but also allows for a `background coroutine` so the application can do other things (such as listening for events on an external trigger, like a Redis queue).

Every event that you send or receive is a Python dict, with a predefined format. It’s these event formats that form the basis of the standard, and allow applications to be swappable between servers.

ASGI is also designed to be a superset of `WSGI` so you can run `WSGI apps` inside `ASGI` servers.
This need a translation wrapper but no that hard.

The async syntax in the `__call__` method, which explicitly marks it as a possible point of task-switches, and allows other asynchronous code to be used within that execution context.
The `receive and send` parameters, over which the messaging between the server and application takes place.
