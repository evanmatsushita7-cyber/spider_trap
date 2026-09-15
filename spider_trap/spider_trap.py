import random

from flask import Flask
app = Flask(__name__)


def random_page():
    links = []

    for i in range(5):
        ending = random.randint(1000, 9999)
        opener = random.choice(["weaver", "wolf", "funnel", "jumping", "cellar"])
        page = f"{opener}{ending}"
        links.append(f'<a href="/{page}">{page}</a><br>')
    links = ''.join(links)
    return links


@app.route("/")
def start():
    fakelinks = random_page()

    return f"""
    <html>
        <body>
            {fakelinks}
        </body>
    </html>
    """


@app.route("/<page_name>")
def trap_site(page_name):
    fakelinks = random_page()

    return f"""
    <html>
        <body>
            {fakelinks}
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)