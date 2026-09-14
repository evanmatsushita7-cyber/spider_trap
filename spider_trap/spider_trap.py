from flask import Flask

app = Flask(__name__)

@app.route("/")
def link():
    spiderwebs = [
        {"name": "Weaver", "url": "golden"},
        {"name": "Cellar", "url": "fakesite"},
        {"name": "Jumping", "url": "notreal"},
        {"name": "Funnel", "url": "lielielie"},
        {"name": "Wolf", "url": "https://example.com"}
    ]

    links = ""

    for spiderweb in spiderwebs:
        links += f'<a href="{spiderweb["url"]}">{spiderweb["name"]}</a><br>'

    return links


@app.route("/golden")
def golden():
    return "<h1>Welcome to the Golden Web</h1>"


@app.route("/fakesite")
def fakesite():
    return "<h1>Fake Site</h1>"


@app.route("/notreal")
def notreal():
    return "<h1>Not Real</h1>"


@app.route("/lielielie")
def lielielie():
    return "<h1>Lie Lie Lie</h1>"


if __name__ == "__main__":
    app.run(debug=True)