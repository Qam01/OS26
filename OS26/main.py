import tkinter as tk
from gui_app import OSSimulatorGUI

def main():
    root = tk.Tk()
    app = OSSimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
