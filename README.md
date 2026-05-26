# RokuPyRemote

A desktop remote control for Roku TVs (and any Roku device), built with Python and tkinter. It uses Roku's [External Control Protocol (ECP)](https://developer.roku.com/docs/developer-program/debugging/external-control-api.md) to send commands over your local network.

![Python](https://img.shields.io/badge/Python-3.x-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

## Features

- **D-pad navigation** -- Up, Down, Left, Right, OK/Select
- **Media controls** -- Play/Pause, Rewind, Fast Forward
- **Volume** -- Volume Up, Volume Down, Mute
- **Power** -- Power On / Power Off
- **Input switching** -- HDMI 1-3, TV Tuner
- **App shortcuts** -- Netflix, YouTube, Prime Video, Disney+
- **Keyboard shortcuts** -- Arrow keys, Enter, Backspace, Space, +/-, M, Escape
- **Customizable key bindings** -- Remap any button via the built-in settings page
- **Remembers your TV's IP and key bindings** between sessions
- **No dependencies** beyond the Python standard library (tkinter)

## Getting Started

### Run from source

```
python roku_remote.py
```

Enter your Roku TV's local IP address (e.g. `192.168.1.42`) and click **Connect**.

### Build a standalone `.exe` (Windows)

Double-click `build_exe.bat` or run it from a terminal. It installs [PyInstaller](https://pyinstaller.org) and produces a single `dist/roku_remote.exe` you can run without Python installed.

## Keyboard Shortcuts

| Key | Action |
|---|---|
| Arrow keys | D-pad navigation |
| Enter | Select / OK |
| Backspace | Back |
| Escape | Home |
| Space | Play / Pause |
| `+` / `=` | Volume Up |
| `-` | Volume Down |
| `M` | Mute |

These are the defaults. Keyboard shortcuts are disabled while the IP address field is focused.

### Customizing Key Bindings

Click the **⚙ Keys** button next to the title to open the key bindings settings. Click any field and press the key you want to assign. Use the **✕** button to remove a binding. Changes are saved to `~/.roku_remote_config.json` and persist across sessions.

## Development

For auto-reloading during development (requires `pip install watchdog`):

```
python dev.py
```

This watches all `.py` files and restarts the app on save.

## How It Works

The app sends HTTP POST requests to port 8060 on your Roku device, which is the standard ECP endpoint. No pairing or authentication is required -- the device just needs to be on the same local network.

## License

This project does not currently specify a license.
