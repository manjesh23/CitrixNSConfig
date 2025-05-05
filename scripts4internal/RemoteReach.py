import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO
import json
import os
import subprocess
import socket
import threading
import requests
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

ICON_URL = "https://www.netscaler.com/etc/designs/netscaler/ns-favicon-medium.png"
SERVER_FILE = "servers.json"

class ServerManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RemoteReach")
        self.root.geometry("600x600")
        self.root.resizable(False, False)
        self.style = ttkb.Style(theme="darkly")
        self.set_app_icon()
        self.servers = self.load_servers()
        self.selected_ip = None
        self.server_status = {}
        self.button_frame = ttkb.Frame(self.root, padding=10)
        self.button_frame.pack(fill=tk.X)
        self.filter_frame = ttkb.Frame(self.root, padding=10)
        self.filter_frame.pack(fill=tk.X)
        self.filter_var = tk.StringVar()
        self.filter_entry = ttkb.Entry(self.filter_frame, textvariable=self.filter_var)
        self.filter_entry.insert(0, "Filter by IP or Username")
        self.filter_entry.bind("<FocusIn>", self.remove_placeholder)
        self.filter_entry.bind("<FocusOut>", self.add_placeholder)
        self.filter_entry.bind("<KeyRelease>", self.filter_servers)
        self.filter_entry.pack(fill=tk.X, padx=5)
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttkb.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttkb.Frame(self.canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        ttkb.Button(self.button_frame, text="Add Server", command=self.add_server).pack(side=tk.LEFT, padx=5)
        ttkb.Button(self.button_frame, text="Remove Server", command=self.remove_server).pack(side=tk.LEFT, padx=5)
        self.server_rows = {}
        self.load_server_list()
        self.schedule_port_check()

    def set_app_icon(self):
        try:
            response = requests.get(ICON_URL, timeout=2)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).convert("RGBA").resize((32, 32), Image.LANCZOS)
        except Exception:
            image = self.generate_no_internet_icon()
        self.tk_icon = ImageTk.PhotoImage(image)
        self.root.iconphoto(False, self.tk_icon)

    def generate_no_internet_icon(self):
        img = Image.new("RGBA", (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((4, 4, 28, 28), fill=(255, 0, 0, 180))
        draw.line((8, 8, 24, 24), fill=(255, 255, 255, 255), width=3)
        return img

    def load_servers(self):
        if os.path.exists(SERVER_FILE):
            with open(SERVER_FILE, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict) or data.get("designed_by") != "Manjesh N":
                        messagebox.showerror("Unauthorized", "This app was designed by Manjesh N.\nModification of server.json not allowed.")
                        self.root.destroy()
                        exit()
                    return data.get("servers", [])
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load server list: {e}")
                    self.root.destroy()
                    exit()
        return []

    def save_servers(self):
        data = {"designed_by": "Manjesh N", "servers": self.servers}
        with open(SERVER_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_server_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.server_rows.clear()
        for server in self.servers:
            self.create_server_row(server)

    def create_server_row(self, server):
        ip = server['ip']
        frame = ttkb.Frame(self.scrollable_frame, padding=5)
        frame.pack(fill=tk.X, pady=2)
        frame.bind("<Button-1>", lambda e, ip=ip: self.select_server(ip))
        ssh_btn = ttkb.Button(frame, text="SSH", width=6, command=lambda: self.connect_ssh(server))
        ssh_btn.pack(side=tk.LEFT, padx=2)
        rdp_btn = ttkb.Button(frame, text="RDP", width=6, command=lambda: self.connect_rdp(server))
        rdp_btn.pack(side=tk.LEFT, padx=2)
        label = ttkb.Label(frame, text=f"{ip} - {server['username']}", anchor=tk.W)
        label.pack(side=tk.LEFT, padx=10)
        label.bind("<Button-1>", lambda e, ip=ip: self.select_server(ip))
        self.server_rows[ip] = {"frame": frame, "ssh_btn": ssh_btn, "rdp_btn": rdp_btn, }

        if ip not in self.server_status:
            self.server_status[ip] = {"ssh": None, "rdp": None}
        self.update_button_style(ssh_btn, self.server_status[ip]["ssh"])
        self.update_button_style(rdp_btn, self.server_status[ip]["rdp"])
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def select_server(self, ip):
        self.selected_ip = ip
        for row_ip, row in self.server_rows.items():
            row["frame"].config(style="primary.TFrame" if row_ip == ip else "TFrame")

    def add_server(self):
        ip = simpledialog.askstring("Add Server", "Enter server IP:", parent=self.root)
        if not ip:
            return
        self.root.after(100, lambda: self.ask_username(ip))
    def ask_username(self, ip):
        username = simpledialog.askstring("Add Server", "Enter username:", parent=self.root)
        if not username:
            return
        self.root.after(100, lambda: self.ask_password(ip, username))
    def ask_password(self, ip, username):
        password = simpledialog.askstring("Add Server", "Enter password:", show='*', parent=self.root)
        if not password:
            return
        server = {"ip": ip, "username": username, "password": password}
        self.servers.append(server)
        self.save_servers()
        self.create_server_row(server)

    def remove_server(self):
        if self.selected_ip is None:
            messagebox.showwarning("Remove Server", "No server selected.", parent=self.root)
            return
        self.servers = [s for s in self.servers if s['ip'] != self.selected_ip]
        self.server_status.pop(self.selected_ip, None)
        self.save_servers()
        self.load_server_list()
        self.selected_ip = None

    def connect_ssh(self, server):
        putty_path = r"C:\\Program Files\\PuTTY\\putty.exe"
        threading.Thread(target=self.run_ssh, args=(putty_path, server), daemon=True).start()

    def run_ssh(self, putty_path, server):
        subprocess.run([putty_path, f"{server['username']}@{server['ip']}", "-pw", server['password']])

    def connect_rdp(self, server):
        threading.Thread(target=self.launch_rdp, args=(server,), daemon=True).start()

    def launch_rdp(self, server):
        try:
            subprocess.run(["cmdkey", "/generic:TERMSRV/" + server['ip'], "/user:" + server['username'], "/pass:" + server['password']], check=True)
            subprocess.run(["mstsc", "/v:" + server['ip']])
        except Exception as e:
            messagebox.showerror("RDP Error", f"Failed to connect: {e}")

    def schedule_port_check(self):
        threading.Thread(target=self.check_ports, daemon=True).start()
        self.root.after(10000, self.schedule_port_check)

    def check_ports(self):
        for server in self.servers:
            threading.Thread(target=self.check_and_update, args=(server,), daemon=True).start()

    def check_and_update(self, server):
        ip = server['ip']
        ssh_ok = self.check_port(ip, 22)
        rdp_ok = self.check_port(ip, 3389)
        if ip in self.server_rows:
            if self.server_status[ip]['ssh'] != ssh_ok:
                self.server_status[ip]['ssh'] = ssh_ok
                self.root.after(0, self.update_button_style, self.server_rows[ip]['ssh_btn'], ssh_ok)
            if self.server_status[ip]['rdp'] != rdp_ok:
                self.server_status[ip]['rdp'] = rdp_ok
                self.root.after(0, self.update_button_style, self.server_rows[ip]['rdp_btn'], rdp_ok)

    def update_button_style(self, button, status):
        if button and button.winfo_exists():
            style = "success.TButton" if status else "danger.TButton"
            button.config(style=style)

    def check_port(self, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((ip, port))
            return True
        except:
            return False

    def filter_servers(self, event=None):
        filter_text = self.filter_var.get().lower()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.server_rows.clear()
        filtered_servers = [server for server in self.servers if filter_text in server["ip"].lower() or filter_text in server["username"].lower()]
        for server in filtered_servers:
            self.create_server_row(server)

    def remove_placeholder(self, event):
        if self.filter_entry.get() == "Filter by IP or Username":
            self.filter_entry.delete(0, tk.END)

    def add_placeholder(self, event):
        if not self.filter_entry.get():
            self.filter_entry.insert(0, "Filter by IP or Username")

if __name__ == "__main__":
    root = ttkb.Window(themename="darkly")
    app = ServerManagerApp(root)
    root.mainloop()

