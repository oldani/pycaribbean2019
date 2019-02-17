## `{Routing}`

`https://github.com/` <!-- .element: class="fragment" -->
`https://github.com/{username}` <!-- .element: class="fragment" -->
`https://github.com/{username}/{repository}` <!-- .element: class="fragment" -->

notes:
Real apps are have many parts/functions, and Web frameworks almost universally route different URLs to each function. For example

1. Recent activity
2. Profile overview
3. User repository

Match Based routing
- a routing table mapping URL patterns to callables/objects
  - tables vs decorators or both
  - regexes vs simpler patterns

Most Python web frameworks do match-based routing.
There is also OBJECT TRAVERSAL witch fell out of favor because 
“explicit is better than implicit”


+++

### Match Based routing <!-- .element: class="fragment" -->
```python
routes = {
  "/": index,
  "/{username}": get_user,
  "/{username}/post/{id}": get_user_post
}
```
<!-- .element: class="fragment" -->


+++

### Object Traversal routing <!-- .element: class="fragment" -->

```python
              "/user/myuser/repo/pycaribbean"
                          == 
          users.get("myuser").repo.get("pycaribbean")
```
<!-- .element: class="fragment" -->


---

#### `Next stop`
```python
from thord import API

app = API()

@app.route("/")
def index(req) -> dict:
    return {"hello": "Welcome to PyCaribbean"}

@app.route("/hello/{name}")
async def hello(req, name: str) -> dict:
    return {"hello": name}

@app.route("/repo/{idx}/issues/{label}")
async def get_repo_issues(req, idx: int, label: str):
    ...
    return {
        "repository": idx, "label": label,
        "issues": [
            {"name": "Add methods views", "content": "Would ..."},
            {"name": "GraphQL support", "content": "Hi, ..."},],
    }

```
<!-- .element: class="stretch stretch-plus" -->
notes:
A lot's stuff going on here for routing
I want users to use simple patterns instead or regex.

*note* Even though we're specifying parameters types, we're not there yet


+++

### `Let's see under the hood`


+++

```python
import re
import inspect
from functools import lru_cache
from urllib.parse import parse_qs, + urlparse +

class NotFound(Exception):
    pass

```
notes:

re because users wont use regex but we must.
All routing system out there use regex under the hood:
  - Flask
  - Django
  - Falcon
  - Starlette

Inpect for been able to define async or normal functions for views
this module help you a lot when for getting info about user code

lru_cache for saving some computing resouces

urlparse for parsing urls


+++

#### If we're going to match path with patterns we need access to url path. <!-- .element: class="fragment" -->

```python
self.path = scope["path"]
```
<!-- .element: class="fragment" -->

```python
class URL:
    def __init__(self, scope) -> None:
        path: str = f"{scope['root_path']}{scope['path']}"
        self._url: str = (
            f"{scope['scheme']}://{scope['server'][0]}:\
                {scope['server'][1]}"
            f"{path}?{scope['query_string'].decode()}"
        )
        self.url = urlparse(self._url)
    ...
    def __getattr__(self, name: str) -> str:
        return getattr(self.url, name)

class Request:
    def __init__(self, scope, receive):
        ...
        self.url: URL = URL(scope)
```
<!-- .element: class="fragment" -->

notes:

Decided to add URL obj to my request


+++

### `Next`

```python
class API:
    def __init__(self) -> None:
        self._routes: dict = {}
    ...
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
```
<!-- .element: class="fragment" -->

```python
                    "user/{id}" != "user/1"
```
<!-- .element: class="fragment" -->

notes:

Add self._routes. It's a dict
We ensure no repeated patterns matching different views

Our keys would be the route obj (which must be hashble)
and our values will be our views.

Then if patterns are no equal to paths we will need to iterate over our
dict, the why not just a list of tuples. Also BigO notation.
More on this latter


our @route decorator, how does decorators works?


+++

### `Let's look the route class` <!-- .element: class="fragment" -->

```python
class Route:
    _pattern = re.compile("{([^{}]*)}")

    def __init__(self, route: str) -> None:
        self.route = route
        self.setup_route()
    ...
    def setup_route(self):
        self._regex = re.compile(
            f"^{self._pattern.sub(self.replace_field,
                                  self.route)}$"
        )

    @staticmethod
    def replace_field(match):
        return f"(?P<{match.group(1)}>[^/]+?)"
```
<!-- .element: class="fragment" -->


                      "/repo/{idx}/issues/{label}" 
                                  == 
            "^/repo/(?P<id>[^/]+?)/issues/(?P<label>[^/]+?)$
<!-- .element: class="fragment" -->

notes:
setup_route: Create a regex for matching incoming routes.

_pattern is a rx for matching {fields} in views patterns.

_pattner.sub calls Route.replace_field in each match

and replace it for group capturing rx. 
/test/{id} will be compile to ^/test/(?P<id>[^/]+?)$


+++

```python
    def __hash__(self):
        return hash(self._regex)

    def match(self, _str: str):
        """ March a path with this routes.
            @return:
                - dict {field: value} for routes with fields.
                - True if matched but no field
                - None for no matches. """
        result = self._regex.match(_str)
        if result:
            return result.groupdict() or True
```

notes:


+++

#### `Back to our API class`

```python
class API:
    ...
    async def handle_request(self, receive, send) -> None:
        req = Request(self.scope, receive)
        try:
            response = await self.dispatch(req)
        except NotFound:
            response = Response("Not found", status_code=404)
        await response(send)
    ...
```


+++

```python

async def dispatch(self, req):
    view, params = self.get_view(req.url.path)
```
<!-- .element: class="fragment" -->
```python
@lru_cache(maxsize=256) # If we already saw this path cache it
def get_view(self, path):
    _view, params = None, {}
    for route, view in self._routes.items():
        match = route.match(path)
        if not match:
            continue
        # Means route have parameters
        if match and isinstance(match, dict):
            _view, params = view, match
        else:
            _view = view
        break
    return _view, params
```
<!-- .element: class="fragment fade-in-then-out" -->
```python
if not view:
    raise NotFound()
if inspect.iscoroutinefunction(view):
    respose = await view(req, **params)
else:
    respose = view(req, **params) # Run this in a threadpool
return Response(respose)
```
<!-- .element: class="fragment" -->
