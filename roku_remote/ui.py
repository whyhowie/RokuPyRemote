import os
import sys
import tkinter as tk

from .config import load_ip, load_keybindings, FRIENDLY_KEY_NAMES
from .network import send_command, connect
from .keybind_dialog import open_keybind_settings
from .theme import (
    BG, PANEL, BTN_BG, BTN_ACTIVE, ACCENT,
    POWER_ON, POWER_OFF, MUTE_BG, FG, MUTED_FG, APPS,
)


class RokuRemote:
    def __init__(self, root):
        self.root = root
        root.title("Roku Remote")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._set_window_icon()

        self.ip_var = tk.StringVar(value=load_ip())
        self.status_var = tk.StringVar(value="Enter your TV's IP and click Connect")
        self.keybindings = load_keybindings()
        self.key_labels = {}
        self.btn_widgets = {}

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

    def _ip(self):
        return self.ip_var.get().strip()

    def _set_window_icon(self):
        try:
            base = getattr(sys, "_MEIPASS",
                           os.path.dirname(os.path.abspath(__file__)))
            ico = os.path.join(base, "roku_remote.ico")
            if not os.path.exists(ico):
                ico = os.path.join(os.path.dirname(base), "roku_remote.ico")
            if os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass

    def send_key(self, key, label=None):
        send_command(self._ip(), "keypress/" + key, label or key, self._set_status)

    def launch_app(self, app_id, label):
        send_command(self._ip(), "launch/" + app_id, label, self._set_status)

    def _connect(self):
        connect(self._ip(), self._set_status)

    # ---------------------------------------------------------------- UI helpers
    def _btn(self, parent, text, key=None, cmd=None, bg=BTN_BG, fg=FG,
             width=5, font=("Segoe UI Symbol", 14)):
        action = cmd if cmd else (lambda k=key: self.send_key(k))

        def pressed_action():
            self._flash_btn(wrapper, b, hint, bg)
            action()

        wrapper = tk.Frame(parent, bg=bg, cursor="hand2")
        b = tk.Button(wrapper, text=text, command=pressed_action, width=width,
                      bg=bg, fg=fg, activebackground=BTN_ACTIVE,
                      activeforeground=FG, relief="flat", bd=0, font=font,
                      cursor="hand2", padx=8, pady=0)
        b.pack(side="top", fill="x")
        hint_text = ""
        if key and key in self.keybindings:
            bound = self.keybindings[key]
            hint_text = FRIENDLY_KEY_NAMES.get(bound, bound)
        hint = tk.Label(wrapper, text=hint_text, bg=bg, fg=MUTED_FG,
                        font=("Segoe UI", 11), cursor="hand2", pady=0)
        hint.pack(side="top", fill="x")
        if key and key in self.keybindings:
            self.key_labels[key] = hint
        if key:
            self.btn_widgets[key] = (wrapper, b, hint, bg)
        hint.bind("<Button-1>", lambda e: pressed_action())
        wrapper.bind("<Button-1>", lambda e: pressed_action())
        return wrapper

    def _flash_btn(self, wrapper, btn, hint, orig_bg):
        wrapper.config(bg=BTN_ACTIVE)
        btn.config(bg=BTN_ACTIVE)
        hint.config(bg=BTN_ACTIVE)
        self.root.after(120, lambda: (
            wrapper.config(bg=orig_bg),
            btn.config(bg=orig_bg),
            hint.config(bg=orig_bg),
        ))

    def _section(self):
        f = tk.Frame(self.root, bg=BG)
        f.pack(fill="x", padx=18, pady=(0, 8))
        return f

    # ---------------------------------------------------------------- sections
    def _build_header(self):
        head = tk.Frame(self.root, bg=BG)
        head.pack(fill="x", padx=18, pady=(16, 10))

        title_row = tk.Frame(head, bg=BG)
        title_row.pack(fill="x")
        tk.Label(title_row, text="Roku Remote", bg=BG, fg=FG,
                 font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Button(title_row, text="⚙ Keys",
                  command=self._open_keybind_settings,
                  bg=PANEL, fg=MUTED_FG, activebackground=BTN_ACTIVE,
                  activeforeground=FG, relief="flat", bd=0,
                  font=("Segoe UI", 9), cursor="hand2",
                  padx=8, pady=2).pack(side="right")

        row = tk.Frame(head, bg=BG)
        row.pack(fill="x", pady=(8, 0))
        tk.Label(row, text="TV IP", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self.ip_entry = tk.Entry(row, textvariable=self.ip_var, width=16,
                                 bg=PANEL, fg=FG, insertbackground=FG,
                                 relief="flat", font=("Consolas", 12))
        self.ip_entry.pack(side="left", ipady=4, padx=(0, 8))
        self.ip_entry.bind("<Return>", lambda e: self._connect())
        tk.Button(row, text="Connect", command=self._connect, bg=ACCENT, fg=FG,
                  activebackground=BTN_ACTIVE, activeforeground=FG, relief="flat",
                  bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2",
                  padx=14, pady=4).pack(side="left")

    def _build_dpad(self):
        f = self._section()
        pad = tk.Frame(f, bg=BG)
        pad.pack()
        self._btn(pad, "▲", "Up").grid(row=0, column=1, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "◀", "Left").grid(row=1, column=0, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "OK", "Select", bg=ACCENT,
                  font=("Segoe UI", 13, "bold")).grid(row=1, column=1, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "▶", "Right").grid(row=1, column=2, padx=4, pady=4, sticky="nsew")
        self._btn(pad, "▼", "Down").grid(row=2, column=1, padx=4, pady=4, sticky="nsew")

    def _build_nav(self):
        f = self._section()
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "↩ Back", "Back", width=7,
                  font=("Segoe UI", 11)).pack(side="left", padx=4)
        self._btn(row, "⌂ Home", "Home", width=7,
                  font=("Segoe UI", 11)).pack(side="left", padx=4)
        self._btn(row, "✱", "Info", width=4,
                  font=("Segoe UI", 11)).pack(side="left", padx=4)
        self._btn(row, "↺ Replay", "InstantReplay", width=8,
                  font=("Segoe UI", 11)).pack(side="left", padx=4)

    def _build_transport(self):
        f = self._section()
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "⏪", "Rev", width=7).pack(side="left", padx=4)
        self._btn(row, "⏯", "Play", width=7).pack(side="left", padx=4)
        self._btn(row, "⏩", "Fwd", width=7).pack(side="left", padx=4)

    def _build_volume(self):
        f = self._section()
        tk.Label(f, text="Volume", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 2))
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "−  Vol", "VolumeDown", bg=ACCENT, width=8,
                  font=("Segoe UI", 13, "bold")).pack(side="left", padx=4)
        self._btn(row, "\U0001F507  Mute", "VolumeMute", bg=MUTE_BG, width=8,
                  font=("Segoe UI", 12)).pack(side="left", padx=4)
        self._btn(row, "Vol  +", "VolumeUp", bg=ACCENT, width=8,
                  font=("Segoe UI", 13, "bold")).pack(side="left", padx=4)

    def _build_power(self):
        f = self._section()
        row = tk.Frame(f, bg=BG)
        row.pack()
        self._btn(row, "⏻  On", "PowerOn", bg=POWER_ON, width=9,
                  font=("Segoe UI", 12, "bold")).pack(side="left", padx=4)
        self._btn(row, "⏻  Off", "PowerOff", bg=POWER_OFF, width=9,
                  font=("Segoe UI", 12, "bold")).pack(side="left", padx=4)

    def _build_inputs(self):
        f = self._section()
        tk.Label(f, text="Inputs", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 2))
        row = tk.Frame(f, bg=BG)
        row.pack()
        for label, key in [("HDMI1", "InputHDMI1"), ("HDMI2", "InputHDMI2"),
                           ("HDMI3", "InputHDMI3"), ("TV", "InputTuner")]:
            self._btn(row, label, key, width=7,
                      font=("Segoe UI", 11)).pack(side="left", padx=4)

    def _build_apps(self):
        f = self._section()
        tk.Label(f, text="Apps", bg=BG, fg=MUTED_FG,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 2))
        row = tk.Frame(f, bg=BG)
        row.pack()
        for name, app_id in APPS:
            self._btn(row, name, cmd=lambda a=app_id, n=name: self.launch_app(a, n),
                      width=8, font=("Segoe UI", 10)).pack(side="left", padx=4)

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
        self._active_bindings = []
        for action, keyname in self.keybindings.items():
            seq = "<{}>".format(keyname)
            self.root.bind(seq, self._kbd(action))
            self._active_bindings.append(seq)
            if keyname == "m":
                self.root.bind("M", self._kbd(action))
                self._active_bindings.append("M")

    def _unbind_keys(self):
        for seq in self._active_bindings:
            self.root.unbind(seq)
        self._active_bindings = []

    def _rebind_keys(self):
        self._unbind_keys()
        self._bind_keys()
        for action, keyname in self.keybindings.items():
            if action in self.key_labels:
                self.key_labels[action].config(
                    text=FRIENDLY_KEY_NAMES.get(keyname, keyname))

    def _kbd(self, key):
        def handler(event):
            if self.root.focus_get() is self.ip_entry:
                return
            if key in self.btn_widgets:
                w, b, h, bg = self.btn_widgets[key]
                self._flash_btn(w, b, h, bg)
            self.send_key(key)
        return handler

    def _open_keybind_settings(self):
        def on_save():
            self._rebind_keys()
            self._set_status("Key bindings saved", ok=True)
        open_keybind_settings(self.root, self.keybindings, on_save)
