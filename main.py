import tkinter as tk
from ui.app import SitramedUI

def main():
    root = tk.Tk()
    app = SitramedUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()