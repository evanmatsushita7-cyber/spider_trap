import random
import time
import json
from flask import Flask
from flask import request
 
max_requests_per_ip = 500
min_requests_for_rate_check = 2
min_request_interval_seconds = 0.3
 

maze_links_per_page = 20
decoy_links_per_page = 5
crosslink_chance = 0.3
max_path_depth = 6

log_file_path = "requests.jsonl"
max_logged_field_length = 200
 
link_id_min = 1000
link_id_max = 9999
link_label_length = 4
 
suspicious_keywords = ["admin", "login", "backup", "config", "wp-", ".env"]
maze_prefixes = ["admin", "wolf", "weaver", "dev", "funnel", "cellar"]
decoy_openers = ["weaver", "wolf", "funnel", "jumping", "cellar", "nav"]
 
confirmed_suspicious_ips = set()
request_times_by_ip = {}
app = Flask(__name__)

def log_request(ip, page_name, action, matched_keyword):
    entry = {
        "ts": time.time(),
        "ip": ip,
        "method": request.method,
        "path": page_name[:max_logged_field_length],
        "user_agent": request.headers.get("User-Agent", "")[:max_logged_field_length],
        "action": action,
        "matched_keyword": matched_keyword,
    }
    with open(log_file_path, "a") as log_file:
        log_file.write(json.dumps(entry) + "\n")
 
def record_request():
    ip = request.remote_addr
    if ip in request_times_by_ip:
        request_times_by_ip[ip].append(time.time())
    else:
        request_times_by_ip[ip] = [time.time()]
def generate_maze_links(page_name):
    maze_links = []
    if random.random() < crosslink_chance:  
        page_name = random.choice(maze_prefixes)
    for _ in range(maze_links_per_page):
        random_suffix = random.randint(link_id_min, link_id_max)
        if page_name.count('/') > max_path_depth:
            page_name = "dev"
        elif page_name.startswith("dev"):
            page_name = "wolf"
        elif page_name.startswith("wolf"):
            page_name = "funnel"
        elif page_name.startswith("funnel"):
            page_name = "cellar"
        elif page_name.startswith("cellar"):
            page_name = "weaver"
        elif page_name.startswith("weaver"):
            page_name = "dev"
 
        child_path = f"{page_name}/{random_suffix}"
        link_html = f'<a href="/{child_path}">{child_path[-link_label_length:]}</a><br>'
        maze_links.append(link_html)
    return ''.join(maze_links)
 
def generate_decoy_links():
    decoy_links = []
    for _ in range(decoy_links_per_page):
        random_suffix = random.randint(link_id_min, link_id_max)
        opener = random.choice(decoy_openers)
        decoy_path = f"{opener}{random_suffix}"
        decoy_links.append(f'<a href="/{decoy_path}">{decoy_path[-link_label_length:]}</a><br>')
    return ''.join(decoy_links)
 
@app.route("/")
def home():
 
    return f"""
    <html>
        <body>
            <a href="/admin" style="display:none;">Admin</a>
            <a href="/about">About</a>
            <a href="/contact">Contact Us</a>
            <a href="/facts">Fun facts</a>
        </body>
    </html>
    """
@app.route("/contact")
def contact():
    return f"""
    <html>
        <body>
            <a href="/about">About</a>
            <a href="/admin" style="display:none;">Admin</a>
            <a href="/facts">Fun facts</a>
            <p>Contact us at 1-800 dot spider</p>
        </body>
    </html>
    """
@app.route("/facts")
def facts():
    return f"""
    <html>
        <body>
            <a href="/about">About</a>
            <a href="/admin" style="display:none;">Admin</a>
            <a href="/contact">Contact Us</a>
            <p>In a given house, there is an average of 10 spiders in every room</p>
        </body>
    </html>
    """
@app.route("/about")
def about():
    return f"""
    <html>
        <body>
            <a href="/contact">Contact Us</a>
            <a href="/admin" style="display:none;">Admin</a>
            <a href="/facts">Fun facts</a>
            <p>We like spiders</p>
        </body>
    </html>
    """
@app.route("/flagged")
def show_flagged():
    flagged_ips = []
    for ip in request_times_by_ip:
        if is_flagged(ip):
            flagged_ips.append(ip)
    return flagged_ips
def is_flagged(ip):
    if ip in confirmed_suspicious_ips:
        return True
    if ip not in request_times_by_ip:
        return False
    if len(request_times_by_ip[ip]) > max_requests_per_ip or (
        len(request_times_by_ip[ip]) >= min_requests_for_rate_check
        and request_times_by_ip[ip][-1] - request_times_by_ip[ip][-2] < min_request_interval_seconds
    ):
        return True
    return False
 
@app.route("/<path:page_name>")
def trap_site(page_name):
    record_request()
    ip = request.remote_addr
    already_flagged = is_flagged(ip)
 
    suspicious = False
    matched_keyword = None 
    for keyword in suspicious_keywords:
        if keyword in page_name:
            suspicious = True
            matched_keyword = keyword 
            confirmed_suspicious_ips.add(ip)
    action = "spider_trap" if (already_flagged or suspicious) else "404"
    log_request(ip, page_name, action, matched_keyword)
 
    if already_flagged or suspicious:
        maze_links = generate_maze_links(page_name)
        decoy_links = generate_decoy_links()
        
        return f"""
        <html>
            <body>
                {maze_links}
                {decoy_links}
            </body>
        </html>
        """
    else:
        return "Not found", 404
@app.route("/robots.txt")
def robots():
    return "User-agent: *\nDisallow: /admin\n", 200, {"Content-Type": "text/plain"}
 
if __name__ == "__main__":
    app.run()
