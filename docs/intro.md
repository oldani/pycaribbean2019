## Let's build an async
## web framework

---

<!-- .slide: data-background-color="#e7ad52" -->
# Hello!
I am Ordanis Sanchez
    - Fullstack web developer 
    - Air traffic controller 


    - Twitter: @ordanisanchez
    - Github: @oldani
<!-- .element: class="whoami" -->


+++

Code & Slides

https://github.com/oldani/pycaribbean2019

notes:

I'm using python 3.6 here. python 3.5 or higher should work.
This won't work on python 2.7 sadly.


+++

> "Reinventing the wheel is great if your goal is to learn more about wheels."
notes:

I expect must of you have develop web app with any web framework out there. Most of dev don’t know exactly what this things are doing under the hood.

Our goal today is to build our own framework and learn exactly what's going on under the hood. What and why? Decisions? Right? Bad?

At the end we should have a very minimal web framework from scratch (0 dependencies); and understand whats going on under the hood.

Initially I have think for it to be a hands on workshop, then a live coding session but we don’t have much time, so I already wrote all the code and will be sharing it with you. So at the end you can catch what’s going on under the hood.


+++

### Agenda:

- Introduction
- Async/Await
- WSGI & WSGI vs ASGI
- Hello PyCaribbean / Hello `{name}`
- Request/Response objects
- Routing
- Where next?


---

<!-- .slide: data-background-color="#C2554F" -->
### What is a Web Framework? <!-- .element: class="fragment" -->
#### `What are the core components?` <!-- .element: class="fragment" -->

notes:
A web framework consists of a set of libraries and a main handler to help you build a web application
Before writing any code with need to know what we gonna build.


+++

<!-- .slide: data-background-color="#C2554F" -->
- Views <!-- .element: class="fragment" -->
- Requests/Response abstractions <!-- .element: class="fragment" -->
- Url routing <!-- .element: class="fragment" -->
- Template engine? What about API driven? <!-- .element: class="fragment" -->
- Data storage <!-- .element: class="fragment" -->
- Development server <!-- .element: class="fragment" -->

notes:
- Views. Generic views like django, functions, class like flask.
- Do we provide requests and different response objects, or dew handle it.
- How are we going to do url routing? Patterns, Regex? Match base or object traversal?
- Do we add templates? Which engine do we use? What about Json response?
- We build our own ORM, use sqlalchemy or let the user choose?
- Do we build it, use one in specific?


+++

<!-- .slide: data-background-color="#C2554F" -->
#### CHOICES WEB FRAMEWORK MAKE <!-- .element: class="fragment" -->



- `Do it your self or not?` <!-- .element: class="fragment" -->
- `WSGI or ASGI?, Websocket support?` <!-- .element: class="fragment" -->
- `Framework or library` <!-- .element: class="fragment" -->
- `Any patther? MVC, MTV, OMW?` <!-- .element: class="fragment" -->

notes:
1. Do we build everything from scratch or use the packages out there?
2. Which specification we use? Do we add support for websocket or maybe http2?
3. Some peoples call Django style like framework and flask like library?
4. Do we enforce our users to use a specific pattern?


---

<!-- .slide: data-background-color="#e7ad52" -->
### This is what we should have at the end <!-- .element: class="fragment" -->


```python
from thord import API

app = API()

@app.route("/")
def index(req) -> dict:
    return {"hello": "Welcome to PyCaribbean"}

async def user(req, idx: int) -> dict:
    return {"id": idx, "name": "test"}

app.add_route("/user/{idx}", user)

if __name__ == '__main__':
    app.run()
```
<!-- .element: class="fragment" -->

notes:
I have already made some choices for this talk.
I want my web framework be like flask (flexible, declarative)
API Driven (not templates)
fstrings like routes
Base on time we may add web sockets support and create a chat.