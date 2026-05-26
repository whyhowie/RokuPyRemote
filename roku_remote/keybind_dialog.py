import tkinter as tk

from .config import (
    DEFAULT_KEYBINDINGS, DEFAULT_FONT_SIZE, FRIENDLY_KEY_NAMES,
    save_keybindings, save_settings,
)
from .theme import BG, PANEL, FG, MUTED_FG, BTN_BG, BTN_ACTIVE, ACCENT, POWER_OFF

ALL_ACTIONS = {
    "Up": "D-pad Up", "Down": "D-pad Down", "Left": "D-pad Left",
    "Right": "D-pad Right", "Select": "OK / Select", "Back": "Back",
    "Home": "Home", "Play": "Play / Pause",
    "VolumeMute": "Mute", "VolumeUp": "Volume Up", "VolumeDown": "Volume Down",
    "Info": "Info", "InstantReplay": "Replay",
    "Rev": "Rewind", "Fwd": "Fast Forward",
    "PowerOn": "Power On", "PowerOff": "Power Off",
    "InputHDMI1": "HDMI 1", "InputHDMI2": "HDMI 2",
    "InputHDMI3": "HDMI 3", "InputTuner": "TV Tuner",
}

SCROLL_HEIGHT = 380


def open_settings(root, keybindings, current_settings, on_save):
    win = tk.Toplevel(root)
    win.title("Settings")
    win.configure(bg=BG)
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()

    fs = current_settings.get("font_size", DEFAULT_FONT_SIZE)

    def _f(offset=0, bold=False):
        style = "bold" if bold else ""
        s = fs + offset
        return ("Segoe UI", s, style) if style else ("Segoe UI", s)

    def _mono(offset=0):
        return ("Consolas", fs + offset)

    # ---- General settings ----
    tk.Label(win, text="Settings", bg=BG, fg=FG,
             font=_f(3, bold=True)).pack(padx=20, pady=(16, 8))

    general = tk.Frame(win, bg=BG)
    general.pack(fill="x", padx=20, pady=(0, 8))

    tray_var = tk.BooleanVar(value=current_settings.get("tray_icon", True))

    tk.Checkbutton(general, text="Minimize to system tray",
                   variable=tray_var, bg=BG, fg=FG,
                   selectcolor=PANEL, activebackground=BG,
                   activeforeground=FG, font=_f(-1),
                   anchor="w").pack(fill="x")

    # Font size
    font_frame = tk.Frame(general, bg=BG)
    font_frame.pack(fill="x", pady=(6, 0))
    tk.Label(font_frame, text="Font size", bg=BG, fg=FG,
             font=_f(-1)).pack(side="left")
    font_var = tk.IntVar(value=fs)
    tk.Spinbox(font_frame, from_=8, to=20, textvariable=font_var, width=4,
               bg=PANEL, fg=FG, font=_mono(-1), relief="flat",
               buttonbackground=BTN_BG, insertbackground=FG,
               justify="center").pack(side="left", padx=(8, 0))
    tk.Label(font_frame, text="(applied on save)", bg=BG, fg=MUTED_FG,
             font=_f(-3)).pack(side="left", padx=(8, 0))

    # ---- Separator ----
    tk.Frame(win, bg=MUTED_FG, height=1).pack(fill="x", padx=20, pady=(8, 8))

    # ---- Key bindings header ----
    tk.Label(win, text="Key Bindings", bg=BG, fg=FG,
             font=_f(1, bold=True)).pack(padx=20, anchor="w")
    tk.Label(win, text="Click a field, then press the key you want to bind.",
             bg=BG, fg=MUTED_FG, font=_f(-2)).pack(padx=20, anchor="w", pady=(0, 8))

    # ---- Scrollable area ----
    scroll_frame = tk.Frame(win, bg=BG, height=SCROLL_HEIGHT)
    scroll_frame.pack(fill="x", padx=20, pady=(0, 4))
    scroll_frame.pack_propagate(False)

    canvas = tk.Canvas(scroll_frame, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=BG)

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>",
                lambda e: canvas.itemconfigure(canvas_window, width=e.width))

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(widget):
        widget.bind("<MouseWheel>", _on_mousewheel)
        for child in widget.winfo_children():
            _bind_mousewheel(child)

    # ---- State ----
    entries = {}
    expanded = [False]

    def _is_assigned(action):
        return bool(keybindings.get(action, ""))

    def _rebuild():
        for widget in inner.winfo_children():
            widget.destroy()
        entries.clear()

        assigned = [a for a in ALL_ACTIONS if _is_assigned(a)]
        unassigned = [a for a in ALL_ACTIONS if not _is_assigned(a)]

        # -- Assigned rows --
        grid = tk.Frame(inner, bg=BG)
        grid.pack(fill="x")

        for i, action in enumerate(assigned):
            label = ALL_ACTIONS[action]
            tk.Label(grid, text=label, bg=BG, fg=FG,
                     font=_f(-1), anchor="w", width=16).grid(
                row=i, column=0, padx=(0, 12), pady=3, sticky="w")

            bound = keybindings.get(action, "")
            var = tk.StringVar(value=FRIENDLY_KEY_NAMES.get(bound, bound))
            raw_var = tk.StringVar(value=bound)

            ent = tk.Entry(grid, textvariable=var, width=12, bg=PANEL, fg=FG,
                           insertbackground=FG, relief="flat", font=_mono(),
                           justify="center", state="readonly",
                           readonlybackground=PANEL)
            ent.grid(row=i, column=1, pady=3)
            entries[action] = (var, raw_var)

            def make_remove(a=action):
                def on_remove():
                    keybindings[a] = ""
                    _rebuild()
                return on_remove

            tk.Button(grid, text="✕", command=make_remove(),
                      bg=BG, fg=POWER_OFF, activebackground=BG,
                      activeforeground=FG, relief="flat", bd=0,
                      font=_f(-2), cursor="hand2",
                      padx=4, pady=0).grid(row=i, column=2, padx=(4, 0), pady=3)

            def make_focus(a=action):
                def on_focus(event):
                    v, rv = entries[a]
                    v.set("...")
                    def on_key(ev):
                        keyname = ev.keysym
                        rv.set(keyname)
                        keybindings[a] = keyname
                        v.set(FRIENDLY_KEY_NAMES.get(keyname, keyname))
                        event.widget.unbind("<Key>")
                    event.widget.bind("<Key>", on_key)
                return on_focus
            ent.bind("<FocusIn>", make_focus())

        # -- Accordion: unassigned --
        if unassigned:
            accordion = tk.Frame(inner, bg=BG)
            accordion.pack(fill="x", pady=(8, 0))

            toggle_frame = tk.Frame(accordion, bg=BG, cursor="hand2")
            toggle_frame.pack(fill="x")
            arrow_lbl = tk.Label(toggle_frame,
                                 text="▾" if expanded[0] else "▸",
                                 bg=BG, fg=MUTED_FG,
                                 font=_f(), cursor="hand2")
            arrow_lbl.pack(side="left")
            text_lbl = tk.Label(toggle_frame,
                                text="Not assigned keys...",
                                bg=BG, fg=MUTED_FG,
                                font=_f(-1), cursor="hand2")
            text_lbl.pack(side="left", padx=(4, 0))

            unassigned_frame = tk.Frame(accordion, bg=BG)

            def toggle():
                expanded[0] = not expanded[0]
                if expanded[0]:
                    arrow_lbl.config(text="▾")
                    unassigned_frame.pack(fill="x", pady=(4, 0))
                    _bind_mousewheel(unassigned_frame)
                    # Auto-scroll to show the accordion content
                    canvas.after(50, lambda: canvas.yview_moveto(1.0))
                else:
                    arrow_lbl.config(text="▸")
                    unassigned_frame.pack_forget()

            for w in (toggle_frame, arrow_lbl, text_lbl):
                w.bind("<Button-1>", lambda e: toggle())

            for action in unassigned:
                label = ALL_ACTIONS[action]

                def make_add(a=action):
                    def on_add():
                        keybindings[a] = DEFAULT_KEYBINDINGS.get(a, "")
                        if not keybindings[a]:
                            keybindings[a] = "?"
                        _rebuild()
                    return on_add

                btn = tk.Button(unassigned_frame, text="+ " + label,
                                command=make_add(),
                                bg=BG, fg=MUTED_FG, activebackground=BTN_ACTIVE,
                                activeforeground=FG, relief="flat", bd=0,
                                font=_f(-1), cursor="hand2",
                                anchor="w", padx=8, pady=3)
                btn.pack(fill="x")

            if expanded[0]:
                unassigned_frame.pack(fill="x", pady=(4, 0))

        _bind_mousewheel(inner)

    _rebuild()
    _bind_mousewheel(scroll_frame)
    _bind_mousewheel(canvas)

    # ---- Bottom buttons ----
    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(pady=(8, 16))

    def save():
        for action, (var, raw_var) in entries.items():
            keybindings[action] = raw_var.get()
        save_keybindings(keybindings)
        save_settings({"tray_icon": tray_var.get(), "font_size": font_var.get()})
        on_save(tray_var.get(), font_var.get())
        win.destroy()

    def reset():
        for action in ALL_ACTIONS:
            keybindings[action] = DEFAULT_KEYBINDINGS.get(action, "")
        tray_var.set(True)
        font_var.set(DEFAULT_FONT_SIZE)
        _rebuild()

    tk.Button(btn_row, text="Reset Defaults", command=reset,
              bg=BTN_BG, fg=FG, activebackground=BTN_ACTIVE,
              activeforeground=FG, relief="flat", bd=0,
              font=_f(-1), cursor="hand2",
              padx=12, pady=6).pack(side="left", padx=6)
    tk.Button(btn_row, text="Save", command=save,
              bg=ACCENT, fg=FG, activebackground=BTN_ACTIVE,
              activeforeground=FG, relief="flat", bd=0,
              font=_f(-1, bold=True), cursor="hand2",
              padx=20, pady=6).pack(side="left", padx=6)
