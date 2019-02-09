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
    return {
        "repository": idx,
        "label": label,
        "issues": [
            {"name": "Add methods views", "content": "Would ..."},
            {"name": "GraphQL support", "content": "Hi, ..."},
        ],
    }
