from __future__ import print_function

from argparse import ArgumentParser
from io import open
import os
from os import chdir, getcwd, listdir
from os.path import abspath, splitext
import sys

import traceback
import logging
from xml.etree.ElementTree import ParseError

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

xmlTemplate = ''
xmlDestino = ''

vodConfigName = ''
TemplateXml = ''
DestinoXml = ''

class MyFrame(Frame):

    _multiples = {
            "Provider_Content_Tier", "Subscriber_View_Limit", "Rating",
            "MSORating", "Advisories", "Audience", "Actors", "Director",
            "Producers", "Category", "Genre", "Chapter", "Recording_Artist",
            "Song_Title", "Languages", "Subtitle_Languages", "Dubbed_Languages"
        }    
    
    def __init__(self, *args, **kwargs):
        global fname
        Frame.__init__(self)
        
        
        self.txtVideoPath = StringVar()
        self.txtXMLTemplate = StringVar()
        self.txtXMLDestination = StringVar()
        self.txtvodConfigfile= StringVar()
        self.MetadataLoeaded = StringVar()
        self.txtVideoPath.set('Browse...')
        self.txtXMLTemplate.set('Browse...')
        self.txtXMLDestination.set('Browse...')
        self.txtvodConfigfile.set('Browse...')
        self.MetadataLoeaded.set('Browse...')
        
        
        self.VarD_Ams = {}
        self.VarD_app = {}
        self.VarD_Content = {}
        
        self.VarD_Ams["GUI"] = {}
        self.VarD_app["GUI"] = {}
        self.VarD_Content["GUI"] = {}
        
        self.master.title("CableLabs VOD Metada 1.1 Generator")
        self.grid(sticky=W+E+N+S)
               
        self.frameMenu = Frame(self)
        self.frameMenu.grid(row=0, column=0, rowspan=2, sticky=(W, N))
        
        self.frameBotones = Frame(self)
        self.frameBotones.grid(row=0, column=1, sticky=(N, W))
        
        self.frameCamposXml = Frame(self)
        self.frameCamposXml.grid(row=1, column=1, sticky=(E, S, N, S))
        
        Label(self.frameMenu, text="GENERATE METADATA", font=("Helvetica", 14,"bold underline")).pack(side=TOP)
        
        Label(self.frameMenu, text="Config File", font=("Helvetica", 9, "bold underline")).pack(side=TOP)
        self.buttonPath = Button(self.frameMenu,textvariable=self.txtvodConfigfile, command=self.load_confg, width=10).pack(fill=X)
        #self.labelFolder = Label(self.frameMenu, font=("Helvetica", 7), textvariable=self.txtvodConfigfile).pack()
        
        Label(self.frameMenu, text="XML Template", font=("Helvetica", 9, "bold underline")).pack()
        self.buttonPath = Button(self.frameMenu, textvariable=self.txtXMLTemplate, command=self.load_XML, width=10).pack(fill=X)
        #self.labelXmlTemplate = Label(self.frameMenu, font=("Helvetica", 7),textvariable=self.txtXMLTemplate).pack()
        
        Label(self.frameMenu, text="Folder", font=("Helvetica", 9, "bold underline")).pack(side=TOP)
        self.buttonPath = Button(self.frameMenu, textvariable=self.txtVideoPath, command=self.load_file, width=10).pack(fill=X)
        #self.labelFolder = Label(self.frameMenu, font=("Helvetica", 7),textvariable=self.txtVideoPath).pack()
        
        Button(self.frameMenu, text="GENERATE", command=self.FormatUpdate, width=15, font=("Helvetica", 11, "bold"), background="lightgray").pack(fill=X)
        
        
        Label(self.frameMenu, pady=5, text="MODIFY FORMAT", font=("Helvetica", 14, "bold underline")).pack()
        
        Label(self.frameMenu, text="XML Template", font=("Helvetica", 9, "bold underline")).pack()
        self.buttonPath = Button(self.frameMenu, textvariable=self.txtXMLTemplate, command=self.load_XML, width=10).pack(fill=X)
        #self.labelXmlTemplate = Label(self.frameMenu,font=("Helvetica", 7), textvariable=self.txtXMLTemplate).pack()
        
        Label(self.frameMenu, text="XML Destination", font=("Helvetica", 9, "bold underline")).pack()
        self.buttonPath = Button(self.frameMenu, textvariable=self.txtXMLDestination, command=self.load_XMLDestination, width=10).pack(fill=X)
        #self.labelXmlTemplate = Label(self.frameMenu, font=("Helvetica", 7),textvariable=self.txtXMLDestination).pack()

        Button(self.frameMenu, text="FORMAT", command=lambda: self.FormatUpdate(isupdate=False), width=15, background="lightgray", font=("Helvetica", 11, "bold")).pack(fill=X)
        
        Label(self.frameMenu, pady=5, text="UPDATE DATA", font=("Helvetica", 14,"bold underline")).pack()
        
        Label(self.frameMenu, text="XML Metadata", font=("Helvetica", 9, "bold underline")).pack()
        self.buttonPath = Button(self.frameMenu, textvariable=self.txtXMLTemplate, command=self.load_XML, width=10).pack(fill=X)
        #self.labelXmlTemplate = Label(self.frameMenu,font=("Helvetica", 7), textvariable=self.txtXMLTemplate).pack()
        
        Button(self.frameMenu, text="UPDATE", command=lambda: self.FormatUpdate(isupdate=True), width=15, background="lightgray", font=("Helvetica", 11, "bold")).pack(fill=X)
        Label(self.frameMenu, pady=1, text="").pack()
        
        Button(self.frameMenu, text="CLEAN", command=lambda: self.ClearAll(), width=15, background="tomato", font=("Helvetica", 11, "bold")).pack(fill=X)
        
        
    def load_file(self):    
        global fname
        global xmlTemplate
        global DestinoXml
        file_path = askdirectory() + '/'
        if file_path:
            try:
                print("Selected Directory: ", file_path)
                #self.txtVideoPath.set(os.path.splitext(os.path.split(file_path)[1])[0])
                self.frameCamposXml.destroy()
                chdir(file_path)
                vod_config = parse_config(abspath(vodConfigName))
                template_path = abspath(xmlTemplate)
                t = ''
                for file_path in listdir(getcwd()):       
                    file_name, file_ext = splitext(file_path)
                    if file_ext not in vod_config.extensions:
                        continue
                    # Only process movie files (skip previews)
                    if file_name.endswith('_preview'):
                        continue
    
                    t = file_path
                    DestinoXml = generate_metadata(file_path, vod_config,template_path, 1)
                    print("vod_package Generated: ", DestinoXml)
                
                self.txtVideoPath.set(t)
            except ValueError: # <- naked except is a bad idea
                showerror("Open Source File", "ERROR:\n'%s'" % ValueError)
            return
    
    
    def load_confg(self):
        global vodConfigName
        vodConfigName = askopenfilename(filetypes=[('INI Configuration', '.ini')])
        if vodConfigName:
            try:
                print("Archivo Config seleccionado: ", vodConfigName)
                self.txtvodConfigfile.set(os.path.splitext(os.path.split(vodConfigName)[1])[0])
            except: # <- naked except is a bad idea
                showerror("Open Source File", "Failed to read file 1\n'%s'" % fname)
            return
        
    def load_XML(self):    
        global xmlTemplate
        xmlTemplate = askopenfilename(filetypes=[('XML Template', '.xml')])
        if xmlTemplate:
            try:
                self.frameCamposXml.destroy()
                try:
                    self.GetXML(WhatLoad="Template")
                    self.txtXMLTemplate.set(os.path.splitext(os.path.split(xmlTemplate)[1])[0])
                except ParseError:
                    showerror("Error al abrir XML", "Lamentablemente el XML posee un formato invalido.")  
                except Exception as e:
                    logging.error(traceback.format_exc())
            except: # <- naked except is a bad idea
                showerror("Open Source File", "Error Desconocido:\n'%s'" % fname)
            return
    
    def load_XMLDestination(self):    
        global xmlDestino
        xmlDestino = askopenfilename(filetypes=[('XML Destination File', '.xml')])
        if xmlDestino:
            try:
                self.txtXMLDestination.set(os.path.splitext(os.path.split(xmlDestino)[1])[0])
                
                self.GetXML(WhatLoad="Destiny")
            except: # <- naked except is a bad idea
                showerror("Open Source File", "Failed to read file 3\n'%s'" % xmlDestino)
            return
                     
    def CreateXmlGenericFields(self, anXml='null', ParamType=''):
        
        self.GetXML(WhatLoad="Template")
        
        if anXml == 'null':
            anXml = TemplateXml
            
        
        counterCOL1 = 0
        counterCOL2 = 0
        
        self.frameCamposXml.destroy()
        self.frameCamposXml = Frame(self)
        self.frameCamposXml.grid(row=1, column=1)
        
        self.VarD_Ams["GUI"].clear()
        self.VarD_app["GUI"].clear()
        self.VarD_Content["GUI"].clear()
        
        if ParamType in anXml.D_ams.keys(): 
            counterCOL1 += 1
            self.VarD_Ams["GUI"].clear()
            self.VarD_Ams["GUI"][ParamType] = {}
            Label(self.frameCamposXml, text="AMS "+ParamType+":", font=("Helvetica", 9, "bold underline")).grid(row=counterCOL1, column=0, columnspan=2, sticky=(W, N))
            self.VarD_Ams[ParamType] = {}
            for D_amsdata in anXml.D_ams[ParamType]:
                lineas = 1
                largo = 30
                if len(anXml.D_ams[ParamType][D_amsdata]) >= largo or (type([1,2])==type(anXml.D_ams[ParamType][D_amsdata]) and len(anXml.D_ams[ParamType][D_amsdata]) >= 2):
                    lineas = 3
                counterCOL1 += 1
                self.VarD_Ams[ParamType][D_amsdata] = anXml.D_ams[ParamType][D_amsdata]
                Label(self.frameCamposXml, text=D_amsdata).grid(row=counterCOL1, column=0, sticky=(W, N))
                self.VarD_Ams["GUI"][ParamType][D_amsdata] = Text(self.frameCamposXml, height=lineas, width=largo)
                self.VarD_Ams["GUI"][ParamType][D_amsdata].grid(row=counterCOL1, column=1, sticky=(W, N, E))
                self.VarD_Ams["GUI"][ParamType][D_amsdata].insert(END, self.VarD_Ams[ParamType][D_amsdata])
                if ParamType == "package" and D_amsdata == "Product":
                    self.VarD_Ams["GUI"][ParamType][D_amsdata].config(background="yellow")
                
                
        if ParamType in anXml.D_app.keys():
            counterCOL2 += 1
            self.VarD_app["GUI"].clear()
            self.VarD_app["GUI"][ParamType] = {}
            Label(self.frameCamposXml, text="App_Data " + ParamType +":", font=("Helvetica", 9, "bold underline")).grid(row=counterCOL2, column=2, columnspan=2, sticky=(W, N))
            self.VarD_app[ParamType] = {}
            for D_appdata in anXml.D_app[ParamType]:
                lineas = 1
                largo = 40
                if len(anXml.D_app[ParamType][D_appdata]) >= largo or type([1,2])==type(anXml.D_app[ParamType][D_appdata]) or D_appdata in self._multiples:
                    lineas = 3
                counterCOL2 += 1
                self.VarD_app[ParamType][D_appdata] = anXml.D_app[ParamType][D_appdata]
                Label(self.frameCamposXml, text=D_appdata).grid(row=counterCOL2, column=2, sticky=(W, N))
                self.VarD_app["GUI"][ParamType][D_appdata] = Text(self.frameCamposXml, height=lineas, width=largo)
                if type([1,2])==type(anXml.D_app[ParamType][D_appdata]) or D_appdata in self._multiples:
                    self.VarD_app["GUI"][ParamType][D_appdata].config(background="lightgreen")
                
                self.VarD_app["GUI"][ParamType][D_appdata].grid(row=counterCOL2, column=3, sticky=(W, N, E))
                if (type([1,2])==type(anXml.D_app[ParamType][D_appdata])):
                    self.VarD_app["GUI"][ParamType][D_appdata].insert('1.0', '\n'.join(self.VarD_app[ParamType][D_appdata]))
                else:
                    self.VarD_app["GUI"][ParamType][D_appdata].insert('1.0', self.VarD_app[ParamType][D_appdata])
                
            
        if ParamType in anXml.D_content.keys():
            
            counterCOL3 = max(counterCOL1, counterCOL2)
            counterCOL3 += 1
          
            self.VarD_Content["GUI"].clear()
            self.VarD_Content["GUI"][ParamType] = {}
            Label(self.frameCamposXml, text="D_content "+ParamType+":", font=("Helvetica", 9, "bold underline")).grid(row=counterCOL3, column=0, columnspan=4, sticky=(W, N))
            self.VarD_Content[ParamType] = {}
            
            D_contentdata = anXml.D_content[ParamType]
            largo = 40
            counterCOL3 += 1
            self.VarD_Content[ParamType][D_contentdata] = D_contentdata
            Label(self.frameCamposXml, text="Archivo: ").grid(row=counterCOL3, column=0, sticky=(W, N, E))
            self.VarD_Content["GUI"][ParamType][D_contentdata] = Text(self.frameCamposXml, height=1, width=largo)
            self.VarD_Content["GUI"][ParamType][D_contentdata].grid(row=counterCOL3, column=1, columnspan=3, sticky=(W, N, E))
            self.VarD_Content["GUI"][ParamType][D_contentdata].insert(END, self.VarD_Content[ParamType][D_contentdata])
         
            
            


        print("LISTOOOO!!! =D2222", anXml)        
    
    def GetXmlAnalisisButtons(self, anXml='null'):
        global TemplateXml
        
        if anXml == 'null':
            anXml = TemplateXml
        
        if "package" in anXml.D_ams.keys():
            self.buttonGenerateMetadata = Button(self.frameBotones, text="Package", command=lambda: self.CreateXmlGenericFields(anXml = anXml,ParamType='package'), width=10)
            self.buttonGenerateMetadata.grid(row=0, column=0, sticky=(W, N, E))
 
        
        if "title" in anXml.D_ams.keys():
            self.buttonGenerateMetadata = Button(self.frameBotones, text="Title", command=lambda: self.CreateXmlGenericFields(anXml = anXml,ParamType='title'), width=10)
            self.buttonGenerateMetadata.grid(row=0, column=1, sticky=(W, N, E))
            
        if "movie" in anXml.D_ams.keys():
            self.buttonGenerateMetadata = Button(self.frameBotones,  text="Movie", command=lambda: self.CreateXmlGenericFields(anXml = anXml,ParamType='movie'), width=10)
            self.buttonGenerateMetadata.grid(row=0, column=2, sticky=(W, N, E))
            
        if "preview" in anXml.D_ams.keys():
            self.buttonGenerateMetadata = Button(self.frameBotones,  text="Preview", command=lambda: self.CreateXmlGenericFields(anXml = anXml,ParamType='preview'), width=10)
            self.buttonGenerateMetadata.grid(row=0, column=3,sticky=(W, N, E))    
            
        if "poster" in anXml.D_ams.keys():
            self.buttonGenerateMetadata = Button(self.frameBotones, text="Poster", command=lambda: self.CreateXmlGenericFields(anXml = anXml,ParamType='poster'), width=10)
            self.buttonGenerateMetadata.grid(row=0, column=4,sticky=(W, N, E))  
            
        if "box cover" in anXml.D_ams.keys():
            self.buttonGenerateMetadata = Button(self.frameBotones, text="Box Cover", command=lambda: self.CreateXmlGenericFields(anXml = anXml,ParamType='box cover'), width=10)
            self.buttonGenerateMetadata.grid(row=0, column=5, sticky=(W, N, E))    
                                  
    def GetXML(self, WhatLoad=''):
        global xmlTemplate
        global TemplateXml
        global xmlDestino
        global DestinoXml
        
        #global fname
        if WhatLoad == "Template":
            
            template_path = default_template_path
            if xmlTemplate != '':
                template_path = xmlTemplate
            template_path = abspath(template_path)
            
            TemplateXml = MyXML(xml_path=xmlTemplate)
            self.MetadataLoeaded.set("Template Loaded")
            self.GetXmlAnalisisButtons(anXml=TemplateXml)

        if WhatLoad == "Destiny":
            if xmlDestino != '':
                template_path = xmlDestino
            template_path = abspath(template_path)
            DestinoXml = MyXML(xml_path=xmlDestino)
            self.MetadataLoeaded.set("Destiny Loaded")
            
        print("Ready...")    
              
    def ChangeFormat(self, escribir=True):
        
        DestinoXml.FormatXML(TemplateXml)
        if escribir:
            self.WriteFile()
                
    def UpdateValues(self, escribir=True):
        
        NuevosValores = {}
        NuevosValores["D_ams"] = {}
        NuevosValores["D_app"] = {}
        NuevosValores["D_content"] = {}
        
        for ParamType in {"box cover", "poster", "preview", "movie", "title", "package"}:
            if self.VarD_Ams["GUI"].get(ParamType):
                if len(self.VarD_Ams["GUI"][ParamType]) >0:
                    NuevosValores["D_ams"][ParamType] = {}
                    try:
                        for CampoDeTexto in self.VarD_Ams["GUI"][ParamType]:
                            NuevosValores["D_ams"][ParamType][CampoDeTexto] = self.VarD_Ams["GUI"][ParamType][CampoDeTexto].get("1.0",'end-1c')
                    except:
                        print("KeyError: ", "NuevosValores[\"D_ams\"][" + ParamType + "][" +CampoDeTexto + "] con problemas" )
                        pass
                    
            if self.VarD_app["GUI"].get(ParamType):    
                if len(self.VarD_app["GUI"][ParamType]) >0:
                    NuevosValores["D_app"][ParamType] = {}
                    try:
                        for CampoDeTexto in self.VarD_app["GUI"][ParamType]:
                            NuevosValores["D_app"][ParamType][CampoDeTexto] = self.VarD_app["GUI"][ParamType][CampoDeTexto].get("1.0",'end-1c')
                    except:
                        print("KeyError: ", "NuevosValores[\"D_app\"][" + ParamType + "][" +CampoDeTexto + "] con problemas" )
                        pass    
            
            if self.VarD_Content["GUI"].get(ParamType):                 
                if len(self.VarD_Content["GUI"][ParamType]) >0:
                    try: 
                        for CampoDeTexto in self.VarD_Content["GUI"][ParamType]:
                            NuevosValores["D_content"][ParamType] = self.VarD_Content["GUI"][ParamType][CampoDeTexto].get("1.0",'end-1c')        
                    except:
                        print("KeyError: ", "NuevosValores[\"D_content\"][" + ParamType + "][" +CampoDeTexto + "] con problemas" )
                        pass     
        
        DestinoXml.UpdateXml(NuevosValores)
        if escribir:
            self.WriteFile()
        
    def WriteFile(self, thepath='', isrewrite=True):
        if thepath == '':
            theabspath = abspath(DestinoXml.xml_path)
            onlypath = os.path.splitext(os.path.split(theabspath)[0])[0] + "\\"
            fn = os.path.splitext(os.path.split(theabspath)[1])[0]
            outfile_newName = "{}_{}.xml".format(fn, "NEW")
            thepath = onlypath+outfile_newName
            
        s = DestinoXml.write_xml(rewrite=isrewrite)
        with open(thepath, "wb") as outfile:
            _ = outfile.write(s) 
                      
    def FormatUpdate(self, isupdate=False):
        global DestinoXml
        isrewrite=True
        if isupdate:
            if DestinoXml == '':
                DestinoXml = TemplateXml
            isrewrite=False
        else:
            if DestinoXml == '':
                showerror("ERROR", "Por favor seleccione con archivos para generar METADATA")
                return
        
        DestinoXml.FormatXML(TemplateXml)
        self.UpdateValues(escribir=False)
        theabspath = abspath(DestinoXml.xml_path)
        fn = os.path.splitext(os.path.split(theabspath)[1])[0]
        onlypath = os.path.splitext(os.path.split(theabspath)[0])[0] + "\\"
        outfile_newName = "{}{}.xml".format(fn, "")       
        self.WriteFile(thepath=onlypath+outfile_newName, isrewrite=isrewrite)     
        if not isupdate: 
            self.ClearAll()    
            
    def ClearAll(self):
        self.txtVideoPath.set('Browse...')
        self.txtXMLTemplate.set('Browse...')
        self.txtXMLDestination.set('Browse...')
        self.txtvodConfigfile.set('Browse...')
        self.MetadataLoeaded.set('Browse...')
        global xmlTemplate
        global TemplateXml
        global xmlDestino
        global DestinoXml
        global fname
        global vodConfigName
        vodConfigName = ''
        xmlTemplate = ''
        xmlDestino = ''
        fname = ''
        self.frameCamposXml.destroy()
        self.frameBotones.destroy()
        self.frameBotones = Frame(self)
        self.frameBotones.grid(row=0, column=1, sticky=(N, W))
        self.frameCamposXml = Frame(self)
        self.frameCamposXml.grid(row=1, column=1, sticky=(E, S))
        
if __name__ == "__main__":
    root = Tk()
    main = MyFrame(root)
    main.pack(fill="both", expand=True)
    root.mainloop()
    
