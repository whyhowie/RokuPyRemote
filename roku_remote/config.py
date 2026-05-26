import json
import os

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".roku_remote_config.json")

DEFAULT_KEYBINDINGS = {
    "Up": "Up", "Down": "Down", "Left": "Left", "Right": "Right",
    "Select": "Return", "Back": "BackSpace", "Home": "Escape",
    "Play": "space", "VolumeMute": "m",
    "VolumeUp": "equal", "VolumeDown": "minus",
}

FRIENDLY_KEY_NAMES = {
    "Up": "↑", "Down": "↓", "Left": "←", "Right": "→",
    "Return": "Enter", "BackSpace": "Bksp", "Escape": "Esc",
    "space": "Space", "plus": "+", "minus": "-",
    "equal": "=", "KP_Add": "Num+", "KP_Subtract": "Num-",
}


def load_config():
    try:
        with open(CONFIG_PATH) as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_config(data):
    try:
        cfg = load_config()
        cfg.update(data)
        with open(CONFIG_PATH, "w") as fh:
            json.dump(cfg, fh)
    except Exception:
        pass


def load_ip():
    return load_config().get("ip", "")


def save_ip(ip):
    save_config({"ip": ip})


def load_keybindings():
    saved = load_config().get("keybindings", {})
    bindings = dict(DEFAULT_KEYBINDINGS)
    bindings.update(saved)
    return bindings


def save_keybindings(keybindings):
    save_config({"keybindings": keybindings})


DEFAULT_FONT_SIZE = 12

def load_settings():
    cfg = load_config()
    return {
        "tray_icon": cfg.get("tray_icon", True),
        "font_size": cfg.get("font_size", DEFAULT_FONT_SIZE),
    }


def save_settings(settings):
    save_config(settings)
