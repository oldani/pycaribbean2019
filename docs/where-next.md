### `Where next?` <!-- .element: class="fragment" -->


+++

### Missing <!-- .element: class="fragment" -->

    We still does not handle `POST` request.
<!-- .element: class="fragment" -->

    Access to req.headers
<!-- .element: class="fragment" -->

    Enhance our routing system to suport methods filter
<!-- .element: class="fragment" -->

    Add type casting on views params
<!-- .element: class="fragment" -->

    Allow for class method views
<!-- .element: class="fragment" -->

    Test client
<!-- .element: class="fragment" -->

notes:

1. Read incoming req body.
   Allow streaming req, rep
2. For auth f.e
3. We may want one view for `POST` and another for `GET`
4. We were adding types but didn't do that.


+++

## `Most Important` <!-- .element: class="fragment" -->
### Everything else you want it to have <!-- .element: class="fragment fade-up" -->


+++

### `Oh right!` <!-- .element: class="fragment" -->


```python
from thord import Route

def index(req) -> dict:
    return {"hello": "Welcome to PyCaribbean"}

async def hello(req, name: str) -> dict:
    return {"hello": name}

urlspatterns = [
    Route("/", index),
    Route("/hello/{name}", hello)
]
```
<!-- .element: class="fragment" -->


---

<!-- .slide: data-background-color="#e7ad52" -->
### Thanks you everyone!