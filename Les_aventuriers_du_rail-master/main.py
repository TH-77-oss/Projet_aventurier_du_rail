import tkinter as tk
from graphic_interface.interface import GameApp

if __name__ == "__main__":
    players = ['Victor', 'IA']
    root = tk.Tk()
    app = GameApp(root, players)
    root.mainloop()
