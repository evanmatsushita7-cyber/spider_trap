import random
import time
import json
from flask import Flask
from flask import request
 
max_requests_per_ip = 500
min_requests_for_rate_check = 2
min_request_interval_seconds = 0.3

max_tracked_ips = 1000

tarpit_delay_seconds = 5
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
    now = time.time()
    if len(request_times_by_ip) >= max_tracked_ips:
        request_times_by_ip.clear()
    if ip in request_times_by_ip:
        entry = request_times_by_ip[ip]
        entry["prev_time"] = entry["last_time"]
        entry["last_time"] = now
        entry["count"] += 1
    else:
        request_times_by_ip[ip] = {"count": 1, "prev_time": None, "last_time": now}
def generate_maze_links(page_name):
    maze_links = []
    if random.random() < crosslink_chance:   # chance to cross-link
        page_name = random.choice(maze_prefixes)
    for _ in range(maze_links_per_page):
        random_suffix = random.randint(link_id_min, link_id_max)

        if page_name.count('/') > max_path_depth:
            link_prefix = random.choice(maze_prefixes)
        elif random.random() < crosslink_chance:
            link_prefix = random.choice(maze_prefixes)
        else:
            link_prefix = page_name

        child_path = f"{link_prefix}/{random_suffix}"
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
    entry = request_times_by_ip[ip]
    if entry["count"] > max_requests_per_ip:
        return True
    if (
        entry["count"] >= min_requests_for_rate_check
        and entry["prev_time"] is not None
        and entry["last_time"] - entry["prev_time"] < min_request_interval_seconds
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
            break
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
