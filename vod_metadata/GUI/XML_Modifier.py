from __future__ import print_function

from argparse import ArgumentParser
from io import open
from os import chdir, getcwd, listdir
from os.path import abspath, splitext
import sys

from vod_metadata import VodPackage
from vod_metadata.md_gen import generate_metadata
from vod_metadata.config_read import parse_config
from vod_metadata import default_config_path, default_template_path
from vod_metadata.ReadXML import MyXML


from tkinter import *
from tkinter.filedialog import askdirectory 
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter import ttk

from functools import partial

fname = ''
xmlName = ''
vodConfigName = ''


class MyFrame(Frame):
    counter = 0
    def __init__(self, *args, **kwargs):
        global fname
        Frame.__init__(self)
        
        
        self.txtVideoPath = StringVar()
        self.txtXMLTemplate = StringVar()
        self.txtvodConfigfile= StringVar()
        
        
        self.master.title("CableLabs VOD Metada 1.1 Generator")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W+E+N+S)
        
        Label(self, text="Select File Folder").grid(row=0, column=0, sticky=W)
        self.buttonPath = Button(self, text="Browse", command=self.load_file, width=10).grid(row=0, column=1, sticky=E)
        self.labelFolder = Label(self, textvariable=self.txtVideoPath).grid(row=1, column=0, columnspan=2, sticky=(W, N))
        
        
        Label(self, text="Select XML Template").grid(row=2, column=0, sticky=W)
        self.buttonPath = Button(self, text="Browse", command=self.load_XML, width=10).grid(row=2, column=1, sticky=E)
        self.labelXmlTemplate = Label(self, textvariable=self.txtXMLTemplate).grid(row=3, column=0, columnspan=2, sticky=(W, N))
        
        
        
        self.buttonGenerateMetadata = Button(self, text="Generate Metadata", command=self.GetXML, width=20)
        self.buttonGenerateMetadata.grid(row=6, column=1, sticky=E)
        
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
        
    def load_XML(self):    
        global xmlName
        xmlName = askopenfilename(filetypes=[('XML Template', '.xml')])
        if xmlName:
            try:
                print("Selected Xml File: ", xmlName)
                self.txtXMLTemplate.set(xmlName)
            except: # <- naked except is a bad idea
                showerror("Open Source File", "Failed to read file\n'%s'" % fname)
            return
         
    def CreateXmlTemplateFields(self, anXml):
        
        counter = 6
        VariablesD_Ams_package = {}
        VariablesD_app_package = {}
        
        counter += 1
        Label(self, text="AMS Package:").grid(row=counter, column=0, sticky=(W, N))
        
        for D_amsPackage in anXml.D_ams["package"]:
            counter += 1
            VariablesD_Ams_package[D_amsPackage] = StringVar()
            VariablesD_Ams_package[D_amsPackage].set(anXml.D_ams["package"][D_amsPackage])
            Label(self, text=D_amsPackage).grid(row=counter, column=0, sticky=(W, N))
            Entry(self, textvariable=VariablesD_Ams_package[D_amsPackage]).grid(row=counter, column=1, columnspan=2, sticky=(W, N, E))
        
        counter += 1
        Label(self, text="App_Data Package:").grid(row=counter, column=0, sticky=(W, N))
        for D_appPackage in anXml.D_app["package"]:
            counter += 1
            VariablesD_app_package[D_appPackage] = StringVar()
            VariablesD_app_package[D_appPackage].set(anXml.D_app["package"][D_appPackage])
            Label(self, text=D_appPackage).grid(row=counter, column=0, sticky=(W, N))
            Entry(self, textvariable=VariablesD_app_package[D_appPackage]).grid(row=counter, column=1, columnspan=2, sticky=(W, N, E))
        
        
        
        print("LISTOOOO!!! =D2222", anXml)    
        
    def  GetXML(self):
        
        global fname
        global xmlName
        
        
        
        template_path = default_template_path
        if xmlName != '':
            template_path = xmlName
        template_path = abspath(template_path)
        
        elXml = MyXML(xmlName)

        self.CreateXmlTemplateFields(elXml)
        
        print("LISTOOOO!!! =D")    
             
            
if __name__ == "__main__":
    root = Tk()
    main = MyFrame(root)
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()
    
