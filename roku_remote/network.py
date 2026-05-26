import threading
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

from .config import save_ip


def send_command(ip, path, label, on_status):
    if not ip:
        on_status("Enter the TV's IP address first", error=True)
        return
    threading.Thread(
        target=_send_worker, args=(ip, path, label, on_status), daemon=True
    ).start()


def _send_worker(ip, path, label, on_status):
    url = "http://{}:8060/{}".format(ip, path)
    try:
        req = urllib.request.Request(url, data=b"", method="POST")
        urllib.request.urlopen(req, timeout=3)
        on_status("Sent: " + label)
    except urllib.error.URLError:
        on_status(
            "No response from {} - is it on the network?".format(ip), error=True
        )
    except Exception as exc:
        on_status(
            "Failed: {} ({})".format(label, exc.__class__.__name__), error=True
        )


def connect(ip, on_status):
    if not ip:
        on_status("Enter the TV's IP address first", error=True)
        return
    on_status("Connecting to {}...".format(ip))
    threading.Thread(target=_connect_worker, args=(ip, on_status), daemon=True).start()


def _connect_worker(ip, on_status):
    url = "http://{}:8060/query/device-info".format(ip)
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:
            data = resp.read()
        tree = ET.fromstring(data)
        name = (
            tree.findtext("user-device-name")
            or tree.findtext("friendly-device-name")
            or tree.findtext("model-name")
            or "Roku device"
        )
        save_ip(ip)
        on_status("Connected to " + name, ok=True)
    except Exception:
        on_status("Could not reach {}:8060 - check the IP".format(ip), error=True)
