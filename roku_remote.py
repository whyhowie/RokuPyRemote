#!/usr/bin/env python3
"""
Roku Remote - a desktop remote for TCL Roku TVs (and any Roku device)
that speaks Roku's External Control Protocol (ECP) over your local network.

Just run it, type in your TV's local IP, click Connect, and use the buttons
or your keyboard. No extra libraries required - only the Python standard
library (tkinter ships with Python on Windows).

Run:   python roku_remote.py
       (or rename to roku_remote.pyw to launch without a console window)
"""

import json
import os
import threading
import tkinter as tk
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# --- where we remember the last-used IP so you don't retype it ----------------
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".roku_remote_config.json")

# --- colors / look ------------------------------------------------------------
BG          = "#15131f"   # window background
PANEL       = "#221c33"   # panel background
BTN_BG      = "#3a2f57"   # normal button
BTN_ACTIVE  = "#4d3f73"   # button while pressed/hovered
ACCENT      = "#7a4fd6"   # Roku-ish purple accent (D-pad OK, volume)
POWER_ON    = "#2e7d4f"   # green power-on
POWER_OFF   = "#9b3535"   # red power-off
MUTE_BG     = "#5a4a82"
FG          = "#f4f2fb"   # text
MUTED_FG    = "#9a93b3"   # secondary text

# Common Roku channel/app IDs for the shortcut row. Edit freely.
APPS = [
    ("Netflix", "12"),
    ("YouTube", "837"),
    ("Prime", "13"),
    ("Disney+", "291097"),
]


class RokuRemote:
    def __init__(self, root):
        self.root = root
        root.title("Roku Remote")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._set_window_icon()

        self.ip_var = tk.StringVar(value=self._load_ip())
        self.status_var = tk.StringVar(value="Enter your TV's IP and click Connect")

        self._build_header()
        self._build_dpad()
        self._build_nav()
        self._build_transport()
        self._build_volume()
        self._build_power()
        self._build_inputs()
        self._build_apps()
        self._build_status()
        self._bind_keys()

    # ---------------------------------------------------------------- networking
    def _ip(self):
        return self.ip_var.get().strip()

    def _set_window_icon(self):
        """Use the bundled .ico for the title bar / taskbar when available."""
        import sys
        try:
            base = getattr(sys, "_MEIPASS",
                           os.path.dirname(os.path.abspath(__file__)))
            ico = os.path.join(base, "roku_remote.ico")
            if os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass

    def send_key(self, key, label=None):
        """Fire a /keypress/<key> command in the background."""
        self._send("keypress/" + key, label or key)

    def launch_app(self, app_id, label):
        self._send("launch/" + app_id, label)

    def _send(self, path, label):
        ip = self._ip()
        if not ip:
            self._set_status("Enter the TV's IP address first", error=True)
            return
        threading.Thread(
            target=self._send_worker, args=(ip, path, label), daemon=True
        ).start()

    def _send_worker(self, ip, path, label):
        url = "http://{}:8060/{}".format(ip, path)
        try:
            req = urllib.request.Request(url, data=b"", method="POST")
            urllib.request.urlopen(req, timeout=3)
            self._set_status("Sent: " + label)
        except urllib.error.URLError:
            self._set_status("No response from {} - is it on the network?".format(ip),
                             error=True)
        except Exception as exc:
            self._set_status("Failed: {} ({})".format(label, exc.__class__.__name__),
                             error=True)

    def connect(self):
        ip = self._ip()
        if not ip:
            self._set_status("Enter the TV's IP address first", error=True)
            return
        self._set_status("Connecting to {}...".format(ip))
        threading.Thread(target=self._connect_worker, args=(ip,), daemon=True).start()

    def _connect_worker(self, ip):
        url = "http://{}:8060/query/device-info".format(ip)
        try:
            with urllib.request.urlopen(url, timeout=4) as resp:
                data = resp.read()
            tree = ET.fromstring(data)
            name = (tree.findtext("user-device-name")
                    or tree.findtext("friendly-device-name")
                    or tree.findtext("model-name")
                    or "Roku device")
            self._save_ip(ip)
            self._set_status("Connected to " + name, ok=True)
        except Exception:
            self._set_status("Could not reach {}:8060 - check the IP".format(ip),
                             error=True)

    # ---------------------------------------------------------------- config
    def _load_ip(self):
        try:
            with open(CONFIG_PATH) as fh:
                return json.load(fh).get("ip", "")
        except Exception:
            return ""

    def _save_ip(self, ip):
        try:
            with open(CONFIG_PATH, "w") as fh:
                json.dump({"ip": ip}, fh)
        except Exception:
            pass

    # ---------------------------------------------------------------- UI helpers
    def _btn(self, parent, text, key=None, cmd=None, bg=BTN_BG, fg=FG,
             width=4, font=("Segoe UI Symbol", 13)):
        action = cmd if cmd else (lambda k=key: self.send_key(k))
        b = tk.Button(parent, text=text, command=action, width=width,
                      bg=bg, fg=fg, activebackground=BTN_ACTIVE,
                      activeforeground=FG, relief="flat", bd=0, font=font,
                      cursor="hand2", padx=6, pady=8)
        return b

    def _section(self):
        f = tk.Frame(self.root, bg=BG)
        f.pack(fill="x", padx=18, pady=(0, 8))
        return f

    # ---------------------------------------------------------------- sections
    def _build_header(self):
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill="x", padx=18, pady=(16, 10))

        tk.Label(head, text="Roku Remote", bg=BG, fg=FG,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")

        row = tk.Frame(head, bg=BG)
        row.pack(fill="x", pady=(8, 0))
        tk.Label(row, text="TV IP", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.ip_entry = tk.Entry(row, textvariable=self.ip_var, width=16,
                                 bg=PANEL, fg=FG, insertbackground=FG,
                                 relief="flat", font=("Consolas", 12))
        self.ip_entry.pack(side="left", ipady=4, padx=(0, 8))
        self.ip_entry.bind("<Return>", lambda e: self.connect())
        tk.Button(row, text="Connect", command=self.connect, bg=ACCENT, fg=FG,
                  activebackground=BTN_ACTIVE, activeforeground=FG, relief="flat",
                  bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2",
                  padx=14, pady=4).pack(side="left")

    def _build_dpad(self):
        f = self._section()
        pad = tk.Frame(f, bg=BG)
        pad.pack()
        self._btn(pad, "\u25B2", "Up").grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "\u25C0", "Left").grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "OK", "Select", bg=ACCENT,
                  font=("Segoe UI", 11, "bold")).grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "\u25B6", "Right").grid(row=1, column=2, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "\u25BC", "Down").grid(row=2, column=1, padx=4, pady=4, sticky="nsew")

    def _build_nav(self):
        f = self._section()
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "\u21A9 Back", "Back", width=7,
                  font=("Segoe UI", 10)).pack(side="left", padx=4)
        self._btn(row, "\u2302 Home", "Home", width=7,
                  font=("Segoe UI", 10)).pack(side="left", padx=4)
        self._btn(row, "\u2731", "Info", width=4).pack(side="left", padx=4)
        self._btn(row, "\u21BA Replay", "InstantReplay", width=8,
                  font=("Segoe UI", 10)).pack(side="left", padx=4)

    def _build_transport(self):
        f = self._section()
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "\u23EA", "Rev", width=6).pack(side="left", padx=4)
        self._btn(row, "\u23EF", "Play", width=6).pack(side="left", padx=4)
        self._btn(row, "\u23E9", "Fwd", width=6).pack(side="left", padx=4)

    def _build_volume(self):
        f = self._section()
        tk.Label(f, text="Volume", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 2))
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "\u2212  Vol", "VolumeDown", bg=ACCENT, width=7,
                  font=("Segoe UI", 12, "bold")).pack(side="left", padx=4)
        self._btn(row, "\U0001F507  Mute", "VolumeMute", bg=MUTE_BG, width=7,
                  font=("Segoe UI", 11)).pack(side="left", padx=4)
        self._btn(row, "Vol  +", "VolumeUp", bg=ACCENT, width=7,
                  font=("Segoe UI", 12, "bold")).pack(side="left", padx=4)

    def _build_power(self):
        f = self._section()
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "\u23FB  On", "PowerOn", bg=POWER_ON, width=8,
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=4)
        self._btn(row, "\u23FB  Off", "PowerOff", bg=POWER_OFF, width=8,
                  font=("Segoe UI", 11, "bold")).pack(side="left", padx=4)

    def _build_inputs(self):
        f = self._section()
        tk.Label(f, text="Inputs", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 2))
        row = tk.Frame(f, bg=BG)
        row.pack()
        for label, key in [("HDMI1", "InputHDMI1"), ("HDMI2", "InputHDMI2"),
                           ("HDMI3", "InputHDMI3"), ("TV", "InputTuner")]:
            self._btn(row, label, key, width=6,
                      font=("Segoe UI", 10)).pack(side="left", padx=4)

    def _build_apps(self):
        f = self._section()
        tk.Label(f, text="Apps", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 2))
        row = tk.Frame(f, bg=BG)
        row.pack()
        for name, app_id in APPS:
            self._btn(row, name, cmd=lambda a=app_id, n=name: self.launch_app(a, n),
                      width=7, font=("Segoe UI", 9)).pack(side="left", padx=4)

    def _build_status(self):
        bar = tk.Frame(self.root, bg=PANEL)
        bar.pack(fill="x", side="bottom")
        self.status_lbl = tk.Label(bar, textvariable=self.status_var, bg=PANEL,
                                   fg=MUTED_FG, font=("Segoe UI", 9), anchor="w",
                                   padx=12, pady=6)
        self.status_lbl.pack(fill="x")

    def _set_status(self, msg, error=False, ok=False):
        color = POWER_OFF if error else (POWER_ON if ok else MUTED_FG)
        self.root.after(0, lambda: (self.status_var.set(msg),
                                    self.status_lbl.config(fg=color)))

    # ---------------------------------------------------------------- keyboard
    def _bind_keys(self):
        mapping = {
            "<Up>": "Up", "<Down>": "Down", "<Left>": "Left", "<Right>": "Right",
            "<Return>": "Select", "<BackSpace>": "Back", "<Escape>": "Home",
            "<space>": "Play", "m": "VolumeMute", "M": "VolumeMute",
            "<plus>": "VolumeUp", "<KP_Add>": "VolumeUp", "<equal>": "VolumeUp",
            "<minus>": "VolumeDown", "<KP_Subtract>": "VolumeDown",
        }
        for seq, key in mapping.items():
            self.root.bind(seq, self._kbd(key))

    def _kbd(self, key):
        def handler(event):
            # don't trigger remote keys while typing in the IP box
            if self.root.focus_get() is self.ip_entry:
                return
            self.send_key(key)
        return handler


def main():
    root = tk.Tk()
    RokuRemote(root)
    root.mainloop()


if __name__ == "__main__":
    main()
