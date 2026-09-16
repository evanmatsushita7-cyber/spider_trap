import random
import time
from flask import Flask
from flask import request
ip_times = {}
app = Flask(__name__)


def ip_grab():
    ip = request.remote_addr
    if ip in ip_times:
        ip_times[ip].append(time.time())
    else:
        ip_times[ip] = [time.time()]


def random_page():
    links = []
    for i in range(5):
        ending = random.randint(1000, 9999)
        opener = random.choice(["weaver", "wolf", "funnel", "jumping", "cellar"])
        page = f"{opener}{ending}"
        links.append(f'<a href="/wolf/{page}">{page}</a><br>')
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
@app.route("/admin/flagged")
def show_flagged():
    flagged = []
    for ip, counts in ip_times.items():
        if len(ip_times[ip]) > 500 or (len(ip_times[ip]) >= 2 and ip_times[ip][-1] - ip_times[ip][-2] < 0.3):
            flagged.append(ip)
    return flagged
            



@app.route("/wolf/<page_name>")
def trap_site(page_name):
    ip_grab()
    fakelinks = random_page()

    return f"""
    <html>
        <body>
            {fakelinks}
        </body>
    </html>
    """
@app.route("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /wolf/"

if __name__ == "__main__":
    app.run(debug=True)