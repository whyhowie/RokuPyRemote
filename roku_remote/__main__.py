import tkinter as tk
from .ui import RokuRemote


def main():
    root = tk.Tk()
    RokuRemote(root)
    root.mainloop()


if __name__ == "__main__":
    main()
