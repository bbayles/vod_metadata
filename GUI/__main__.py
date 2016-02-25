from __future__ import print_function

from argparse import ArgumentParser
from io import open
from os import chdir, getcwd, listdir
from os.path import abspath, splitext

from vod_metadata import VodPackage
from vod_metadata.md_gen import generate_metadata
from vod_metadata.config_read import parse_config
from vod_metadata import default_config_path, default_template_path

from tkinter import *
from tkinter.filedialog import askdirectory 
from tkinter.messagebox import showerror
from tkinter import ttk

fname = ''


def generateMetadata():
    config_path = default_config_path
    vod_config = parse_config(abspath(config_path))
    
    template_path = default_template_path
    template_path = abspath(template_path)
    
    for file_path in listdir(getcwd()):
        
        file_name, file_ext = splitext(file_path)
        
        if file_ext not in vod_config.extensions:
            continue
        # Only process movie files (skip previews)
        if file_name.endswith('_preview'):
            continue
    
        
        vod_package = generate_metadata(file_path, vod_config, template_path)
        
        s = vod_package.write_xml(rewrite=True)
        with open(vod_package.xml_path, "wb") as outfile:
            _ = outfile.write(s)
    
    print("LISTOOOO!!! =D")


class MyFrame(Frame):
    def __init__(self):
        global fname
        Frame.__init__(self)
        
        self.txtVideoPath = StringVar()
        
        self.master.title("CableLabs VOD Metada 1.1 Generator")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W+E+N+S)
        
        Label(self, text="Seleccione Carpeta con archivos").grid(row=0, column=0, sticky=W)
        self.button = Button(self, text="Browse", command=self.load_file, width=10)
        self.button.grid(row=0, column=1, sticky=E)
        self.labelFolder = Label(self, textvariable=self.txtVideoPath).grid(row=1, column=0, columnspan=2, sticky=(W, N))
        
        self.buttonGenerateMetadata = Button(self, text="Generate Metadata", command=self.GenerateMetadata, width=20)
        self.buttonGenerateMetadata.grid(row=10, column=1, sticky=E)
        
        for child in self.winfo_children(): child.grid_configure(padx=5, pady=5)
        
        
    def load_file(self):    
        global fname
        fname = askdirectory() + '/'
        if fname:
            try:
                print("Selected Directory: ", fname)
                self.txtVideoPath.set(fname)
            except: # <- naked except is a bad idea
                showerror("Open Source File", "Failed to read file\n'%s'" % fname)
            return

    def GenerateMetadata(self):
        global fname
        if fname:
            try:
                print("A generar metadata!", fname)
                chdir(fname)
                generateMetadata()
            except: # <- maybe we can show some more specific error.
                showerror("Error during Metadata Generation")
            return
        else:
            showerror("Error :(", "An error occurred, verify that all fields are completed") 
if __name__ == "__main__":
    #generateMetadata()
    MyFrame().mainloop()
