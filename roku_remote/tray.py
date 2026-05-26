import os
import sys
import threading

try:
    import pystray
    from PIL import Image
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


def _load_icon():
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    ico = os.path.join(base, "roku_remote.ico")
    if not os.path.exists(ico):
        ico = os.path.join(os.path.dirname(base), "roku_remote.ico")
    if os.path.exists(ico):
        return Image.open(ico)
    return Image.new("RGBA", (64, 64), (122, 79, 214, 255))


class TrayIcon:
    def __init__(self, root, on_quit=None):
        self.root = root
        self.on_quit = on_quit
        self.icon = None
        self._thread = None

    @property
    def available(self):
        return TRAY_AVAILABLE

    def start(self):
        if not TRAY_AVAILABLE or self.icon:
            return
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._show, default=True),
            pystray.MenuItem("Quit", self._quit),
        )
        self.icon = pystray.Icon("roku_remote", _load_icon(),
                                 "Roku Remote", menu)
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()
            self.icon = None

    def _show(self, icon=None, item=None):
        self.root.after(0, self._restore_window)

    def _restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _quit(self, icon=None, item=None):
        self.stop()
        self.root.after(0, self._do_quit)

    def _do_quit(self):
        if self.on_quit:
            self.on_quit()
        else:
            self.root.destroy()
