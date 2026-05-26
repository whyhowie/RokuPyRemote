#!/usr/bin/env python3
"""
Roku Remote - a desktop remote for TCL Roku TVs (and any Roku device).

This is the entry point. Run:
    python roku_remote.py
    python -m roku_remote
"""

import tkinter as tk
from roku_remote.ui import RokuRemote


def main():
    root = tk.Tk()
    RokuRemote(root)
    root.mainloop()


if __name__ == "__main__":
    main()
