from __future__ import print_function

from vod_metadata.GUI.XML_Modifier import MyFrame
from tkinter import *

        
if __name__ == "__main__":
    root = Tk()
    main = MyFrame(root)
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()
