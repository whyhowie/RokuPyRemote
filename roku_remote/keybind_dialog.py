import tkinter as tk

from .config import DEFAULT_KEYBINDINGS, FRIENDLY_KEY_NAMES, save_keybindings
from .theme import BG, PANEL, FG, MUTED_FG, BTN_BG, BTN_ACTIVE, ACCENT, POWER_OFF

ACTION_LABELS = {
    "Up": "D-pad Up", "Down": "D-pad Down", "Left": "D-pad Left",
    "Right": "D-pad Right", "Select": "OK / Select", "Back": "Back",
    "Home": "Home", "Play": "Play / Pause",
    "VolumeMute": "Mute", "VolumeUp": "Volume Up", "VolumeDown": "Volume Down",
}


def open_keybind_settings(root, keybindings, on_save):
    win = tk.Toplevel(root)
    win.title("Key Bindings")
    win.configure(bg=BG)
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    tk.Label(win, text="Key Bindings", bg=BG, fg=FG,
             font=("Segoe UI", 14, "bold")).pack(padx=20, pady=(16, 4))
    tk.Label(win, text="Click a field, then press the key you want to bind.",
             bg=BG, fg=MUTED_FG, font=("Segoe UI", 9)).pack(padx=20, pady=(0, 12))

    entries = {}
    container = tk.Frame(win, bg=BG)
    container.pack(padx=20, pady=(0, 8))

    for i, (action, label) in enumerate(ACTION_LABELS.items()):
        tk.Label(container, text=label, bg=BG, fg=FG,
                 font=("Segoe UI", 10), anchor="w", width=14).grid(
            row=i, column=0, padx=(0, 12), pady=3, sticky="w")
        var = tk.StringVar(value=FRIENDLY_KEY_NAMES.get(
            keybindings.get(action, ""), keybindings.get(action, "")))
        ent = tk.Entry(container, textvariable=var, width=10, bg=PANEL, fg=FG,
                       insertbackground=FG, relief="flat", font=("Consolas", 11),
                       justify="center", state="readonly",
                       readonlybackground=PANEL)
        ent.grid(row=i, column=1, pady=3)
        raw_var = tk.StringVar(value=keybindings.get(action, ""))
        entries[action] = (ent, var, raw_var)

        def make_clear_handler(a=action):
            def on_clear():
                e, v, rv = entries[a]
                rv.set("")
                v.set("")
                e.unbind("<Key>")
            return on_clear

        tk.Button(container, text="✕", command=make_clear_handler(),
                  bg=BG, fg=POWER_OFF, activebackground=BG,
                  activeforeground=FG, relief="flat", bd=0,
                  font=("Segoe UI", 9), cursor="hand2",
                  padx=4, pady=0).grid(row=i, column=2, padx=(4, 0), pady=3)

        def make_focus_handler(a=action):
            def on_focus(event):
                e, v, rv = entries[a]
                v.set("...")
                def on_key(ev):
                    keyname = ev.keysym
                    rv.set(keyname)
                    v.set(FRIENDLY_KEY_NAMES.get(keyname, keyname))
                    e.unbind("<Key>")
                e.bind("<Key>", on_key)
            return on_focus
        ent.bind("<FocusIn>", make_focus_handler())

    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(pady=(8, 16))

    def save():
        for action, (ent, var, raw_var) in entries.items():
            keybindings[action] = raw_var.get()
        save_keybindings(keybindings)
        on_save()
        win.destroy()

    def reset():
        keybindings.update(DEFAULT_KEYBINDINGS)
        for action, (ent, var, raw_var) in entries.items():
            key = DEFAULT_KEYBINDINGS.get(action, "")
            raw_var.set(key)
            var.set(FRIENDLY_KEY_NAMES.get(key, key))

    tk.Button(btn_row, text="Reset Defaults", command=reset,
              bg=BTN_BG, fg=FG, activebackground=BTN_ACTIVE,
              activeforeground=FG, relief="flat", bd=0,
              font=("Segoe UI", 10), cursor="hand2",
              padx=12, pady=6).pack(side="left", padx=6)
    tk.Button(btn_row, text="Save", command=save,
              bg=ACCENT, fg=FG, activebackground=BTN_ACTIVE,
              activeforeground=FG, relief="flat", bd=0,
              font=("Segoe UI", 10, "bold"), cursor="hand2",
              padx=20, pady=6).pack(side="left", padx=6)
