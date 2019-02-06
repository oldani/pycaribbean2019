from thord import API

app = API()


@app.add_view
def hello(req):
    return f"Hello {req.args.get('name')}!"
