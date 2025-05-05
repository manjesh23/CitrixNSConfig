import os
import json
import socket
import subprocess
import threading
import time
import webbrowser
from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
app.secret_key = "your-secret-key"

SERVER_FILE = "servers.json"
USER_FILE = "users.json"

# ---------------- Templates ----------------

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - RemoteReach</title>
    <style>
        body {
            background-color: #121212;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: #1e1e1e;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.7);
            width: 320px;
        }
        h2 {
            text-align: center;
            color: #00d1b2;
            margin-bottom: 20px;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            border: none;
            background-color: #2a2a2a;
            color: #eee;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #00d1b2;
            border: none;
            border-radius: 4px;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background-color: #00b89c;
        }
        .error {
            color: #ff5f5f;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>RemoteReach Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required />
            <input type="password" name="password" placeholder="Password" required />
            <button type="submit">Login</button>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>RemoteReach Web</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1c1c1c; color: #eee; padding: 20px; }
        h1 { color: #00d1b2; }
        input, button { padding: 8px; margin: 4px; border-radius: 4px; border: none; }
        input[type="text"], input[type="password"] { width: 180px; }
        .server-row { background: #2a2a2a; padding: 10px; margin: 8px 0; border-radius: 5px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; }
        .server-info { display: flex; flex-grow: 1; justify-content: flex-start; }
        .status-btn { margin: 0 4px; padding: 6px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; }
        .up { background-color: #006400; color: white; }
        .down { background-color: #8b0000; color: white; }
        .btns { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-start; }
    </style>
    <script>
        function filterServers() {
            const filter = document.getElementById("filterInput").value.toLowerCase();
            const rows = document.getElementsByClassName("server-row");
            for (let row of rows) {
                const text = row.getAttribute("data-filter").toLowerCase();
                row.style.display = text.includes(filter) ? "flex" : "none";
            }
        }
        function updateStatus(index) {
            fetch(`/status/${index}`)
                .then(res => res.json())
                .then(data => {
                    const row = document.getElementById(`server-row-${index}`);
                    if (!row) return;
                    const sshBtn = row.querySelector(".ssh-btn");
                    const rdpBtn = row.querySelector(".rdp-btn");
                    const webBtn = row.querySelector(".web-btn");
                    updateButtonClass(sshBtn, data.ssh_status);
                    updateButtonClass(rdpBtn, data.rdp_status);
                    updateButtonClass(webBtn, data.http_status);
                });
        }
        function updateButtonClass(btn, isUp) {
            if (!btn) return;
            btn.classList.remove("up", "down");
            btn.classList.add(isUp ? "up" : "down");
        }
        window.onload = () => {
            const rows = document.getElementsByClassName("server-row");
            for (let i = 0; i < rows.length; i++) {
                updateStatus(i);
            }
            setInterval(() => {
                for (let i = 0; i < rows.length; i++) {
                    updateStatus(i);
                }
            }, 10000);
        };
    </script>
</head>
<body>
    <h1>RemoteReach (Web)</h1>
    <form method="POST" action="/add">
        <input name="ip" placeholder="IP" required>
        <input name="username" placeholder="Username" required>
        <input name="password" placeholder="Password" type="password" required>
        <button type="submit">Add Server</button>
    </form>
    <input id="filterInput" placeholder="Filter by IP or Username" onkeyup="filterServers()" />
    {% for server in servers %}
        <div class="server-row" id="server-row-{{loop.index0}}" data-filter="{{server.ip}} {{server.username}}">
            <div class="btns">
                <a href="/ssh/{{loop.index0}}">
                    <button class="status-btn ssh-btn">SSH</button>
                </a>
                <a href="/rdp/{{loop.index0}}">
                    <button class="status-btn rdp-btn">RDP</button>
                </a>
                <a href="/web/{{loop.index0}}">
                    <button class="status-btn web-btn">Web</button>
                </a>
                <a href="/delete/{{loop.index0}}">
                    <button class="status-btn" style="background-color: #444;">Remove</button>
                </a>
            </div>
            <div class="server-info">
                <strong>{{server.ip}}</strong> - {{server.username}}
            </div>
        </div>
    {% endfor %}
</body>
</html>
"""
# ---------------- Utility Functions ----------------

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE) as f:
            return json.load(f)
    return {"users": []}

def save_users(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_servers():
    if not os.path.exists(SERVER_FILE):
        return []
    with open(SERVER_FILE) as f:
        return json.load(f).get("servers", [])

def save_servers(servers):
    with open(SERVER_FILE, "w") as f:
        json.dump({"servers": servers}, f, indent=2)

def check_port(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=1):
            return True
    except:
        return False

def get_user_data(username):
    users = load_users()
    return next((u for u in users["users"] if u["username"] == username), None)

# ---------------- Routes ----------------

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]["username"]
    user = get_user_data(username)
    servers = [load_servers()[i] for i in user["servers"]]
    return render_template_string(HTML_TEMPLATE, servers=servers, user=user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users_db = load_users()
        user = next((u for u in users_db["users"] if u["username"] == username), None)
        if user and check_password_hash(user["password"], password):
            session["user"] = {"username": user["username"], "role": user["role"]}
            return redirect(url_for("index"))
        return render_template_string(LOGIN_TEMPLATE, error="Invalid username or password")
    return render_template_string(LOGIN_TEMPLATE)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]["username"]
    user = get_user_data(username)
    if user["role"] != "admin":
        return "Only admin can register users"
    if request.method == "POST":
        users = load_users()
        if any(u["username"] == request.form["username"] for u in users["users"]):
            return "Username exists"
        users["users"].append({
            "username": request.form["username"],
            "password": generate_password_hash(request.form["password"]),
            "role": request.form.get("role", "user"),
            "servers": []
        })
        save_users(users)
        return redirect("/")
    return '''
    <h2>Register New User</h2>
    <form method="post">
        <input name="username" placeholder="Username">
        <input name="password" placeholder="Password" type="password">
        <select name="role">
            <option value="user">User</option>
            <option value="admin">Admin</option>
        </select>
        <button type="submit">Register</button>
    </form>
    '''

@app.route("/add", methods=["POST"])
def add_server():
    if "user" not in session:
        return redirect("/login")
    servers = load_servers()
    user = get_user_data(session["user"]["username"])
    new = {
        "ip": request.form["ip"],
        "username": request.form["username"],
        "password": request.form["password"]
    }
    servers.append(new)
    save_servers(servers)

    users = load_users()
    for u in users["users"]:
        if u["username"] == user["username"]:
            u["servers"].append(len(servers) - 1)
            break
    save_users(users)
    return redirect("/")

@app.route("/delete/<int:index>")
def delete_server(index):
    if "user" not in session:
        return redirect("/login")
    servers = load_servers()
    if 0 <= index < len(servers):
        servers.pop(index)
        save_servers(servers)
    return redirect("/")

@app.route("/status/<int:index>")
def status(index):
    servers = load_servers()
    if 0 <= index < len(servers):
        ip = servers[index]["ip"]
        return {
            "ssh_status": check_port(ip, 22),
            "rdp_status": check_port(ip, 3389),
            "http_status": check_port(ip, 80)
        }
    return {"error": "Invalid index"}, 404

@app.route("/ssh/<int:index>")
def ssh(index):
    servers = load_servers()
    if 0 <= index < len(servers):
        server = servers[index]
        threading.Thread(target=lambda: subprocess.run([
            "C:\\Program Files\\PuTTY\\putty.exe",
            f"{server['username']}@{server['ip']}",
            "-pw", server["password"]
        ])).start()
    return redirect("/")

@app.route("/rdp/<int:index>")
def rdp(index):
    servers = load_servers()
    if 0 <= index < len(servers):
        subprocess.Popen(["mstsc", "/v:" + servers[index]["ip"]])
    return redirect("/")

@app.route("/web/<int:index>")
def web(index):
    servers = load_servers()
    if 0 <= index < len(servers):
        server = servers[index]
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        try:
            driver.get(f"http://{server['ip']}/")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(server["username"])
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(server["password"] + Keys.RETURN)
            time.sleep(5)
        except Exception as e:
            print("Error:", e)
    return redirect("/")

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:5000")

def assign_all_servers_to_admin():
    users = load_users()
    servers = load_servers()
    admin = next((u for u in users["users"] if u["role"] == "admin"), None)
    if admin:
        admin["servers"] = list(range(len(servers)))
        save_users(users)

with app.test_request_context():
    session.clear()
assign_all_servers_to_admin()

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    app.run(debug=True, use_reloader=False)
