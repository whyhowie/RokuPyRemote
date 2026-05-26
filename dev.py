"""Auto-reload launcher for development. Restarts on any .py file change.

Usage:  python dev.py
Requires: pip install watchdog
"""

import os
import subprocess
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ENTRY = "roku_remote.py"


class ReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.proc = None
        self.start_app()

    def start_app(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.proc = subprocess.Popen([sys.executable, ENTRY])

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".py"):
            print(f"[dev] {os.path.basename(event.src_path)} changed — restarting...")
            self.start_app()


if __name__ == "__main__":
    handler = ReloadHandler()
    observer = Observer()
    observer.schedule(handler, ".", recursive=True)
    observer.start()
    print(f"[dev] Watching *.py for changes. Save any file to reload.")
    print("[dev] Press Ctrl+C in this terminal to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[dev] Stopping...")
    finally:
        observer.stop()
        if handler.proc and handler.proc.poll() is None:
            handler.proc.terminate()
        observer.join()
