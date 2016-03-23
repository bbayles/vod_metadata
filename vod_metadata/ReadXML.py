'''
Created on 3 de mar. de 2016

@author: nmastromarino
'''
from __future__ import division
from io import open
from vod_metadata.xml_helper import etree,tobytes
import ast
import re

class MissingElement(Exception):
    pass    
    
class MyXML(object):
        
    _multiples = {
            "Provider_Content_Tier", "Subscriber_View_Limit", "Rating",
            "MSORating", "Advisories", "Audience", "Actors", "Director",
            "Producers", "Category", "Genre", "Chapter", "Recording_Artist",
            "Song_Title", "Languages", "Subtitle_Languages", "Dubbed_Languages"
        }
    
    
    def __init__(self, xml_path=None, vod_config=None, NewValuesArray={}):
        
        
        self.xml_path = xml_path
        self.tree = etree.parse(self.xml_path)
            
        self.D_ams = {}
        self.D_app = {}
        self.D_content = {}    
        
        if len(NewValuesArray) > 0:
            self.NewValuesArray = NewValuesArray;
        
        ADI = self.tree.getroot()
        self._read_package(ADI)
        self._read_title(ADI)
        self._read_elements(ADI)
               
    def _read_package(self, ADI):
        package_Metadata = ADI.find("Metadata")
        self.D_ams["package"] = package_Metadata.find("AMS").attrib
        self.D_app["package"] = self._parse_App_Data(package_Metadata)
           
    def _parse_App_Data(self, ae_Metadata):
        D = {}
        for App_Data in ae_Metadata.findall("App_Data"):
            key = App_Data.attrib["Name"]
            value = App_Data.attrib["Value"]
            # Some App_Data fields can occur more than once and are treated as
            # a list
            if value != '':
                if key in self._multiples:
                    if key in D:
                        D[key].append(value)
                    else:
                        D[key] = [value]
                # Others can only occur once and are treated as plain values
                else:
                    D[key] = value
            else:
                D[key] = value
        return D   
    
    def _read_title(self, ADI):
        title_Metadata = ADI.find("Asset").find("Metadata")
        self.D_ams["title"] = title_Metadata.find("AMS").attrib
        self.D_app["title"] = self._parse_App_Data(title_Metadata)  
        
    def _read_elements(self, ADI):
            # Asset elements section: "movie", "preview", "poster", and
            # "box cover" are allowed.
        for ae_Asset in ADI.find("Asset").findall("Asset"):
            ae_Metadata = ae_Asset.find("Metadata")
            ae_AMS = ae_Metadata.find("AMS")
            ae_type = ae_AMS.attrib["Asset_Class"]
            self.D_ams[ae_type] = ae_AMS.attrib
            self.D_app[ae_type] = self._parse_App_Data(ae_Metadata)
            if ae_Asset.find("Content") is not None:
                self.D_content[ae_type] = (
                    ae_Asset.find("Content").attrib["Value"]
                )
     
    def _write_App_Data(self, ae_type, parent_Metadata):
        for key, value in sorted(
            self.D_app[ae_type].items(), key=lambda x: x[0]
        ):
            # Configuration controls whether certain values get skipped
            #if key in self.param_skip:
                #continue
            # Some of the App_Data tags can be repeated
            if key in self._multiples:
                for v in value:
                    ae_App_Data = etree.SubElement(parent_Metadata, "App_Data")
                    ae_App_Data.set("App", self.D_ams["package"]["Product"])
                    ae_App_Data.set("Name", key)
                    ae_App_Data.set("Value", v)
            # Others are only allowed to appear once
            else:
                ae_App_Data = etree.SubElement(parent_Metadata, "App_Data")
                ae_App_Data.set("App", self.D_ams["package"]["Product"])
                ae_App_Data.set("Name", key)
                ae_App_Data.set("Value", value)
                            
    def write_xml(self, rewrite=False):
        # A movie element is required by this library
        if "movie" not in self.D_ams:
            raise MissingElement("Package does not specify a movie element")

        # Over-write the given XML values with the ones determined by scanning
        # the video if needed
        #if rewrite:
            #self.check_files()

        # Root element
        doctype = b'<!DOCTYPE ADI SYSTEM "ADI.DTD">'
        ADI = etree.Element("ADI")

        # Package asset
        package_Metadata = etree.SubElement(ADI, "Metadata")
        package_AMS = etree.SubElement(package_Metadata, "AMS")
        for key, value in sorted(
            self.D_ams["package"].items(), key=lambda x: x[0]
        ):
            package_AMS.set(key, value)
        self._write_App_Data("package", package_Metadata)

        # Title asset
        title_Asset = etree.SubElement(ADI, "Asset")
        title_Metadata = etree.SubElement(title_Asset, "Metadata")
        title_AMS = etree.SubElement(title_Metadata, "AMS")
        for key, value in sorted(
            self.D_ams["title"].items(), key=lambda x: x[0]
        ):
            title_AMS.set(key, value)
        self._write_App_Data("title", title_Metadata)

        # Asset elements
        for ae_type in ("movie", "preview", "poster", "box cover"):
            if ae_type not in self.D_ams:
                continue
            ae_Asset = etree.SubElement(title_Asset, "Asset")
            ae_Metadata = etree.SubElement(ae_Asset, "Metadata")
            # AMS section
            ae_AMS = etree.SubElement(ae_Metadata, "AMS")
            for key, value in sorted(
                self.D_ams[ae_type].items(), key=lambda x: x[0]
            ):
                ae_AMS.set(key, value)
            self._write_App_Data(ae_type, ae_Metadata)
            # Content element, if it is present
            if ae_type in self.D_content:
                ae_Content = etree.SubElement(ae_Asset, "Content")
                ae_Content.set("Value", self.D_content[ae_type])   
                     
        return tobytes(doctype, ADI)                          

    def FormatXML(self, aTemplate):  
        for Each_ams in list(self.D_ams):
            if not (Each_ams in list(aTemplate.D_ams)):
                del self.D_ams[Each_ams]
                break
            
            for values_each_AMS in list(self.D_ams[Each_ams]):
                if not (values_each_AMS in list(aTemplate.D_ams[Each_ams])):
                    del self.D_ams[Each_ams][values_each_AMS]
                
        for Each_Template_ams in list(aTemplate.D_ams):
            if not (Each_Template_ams in list(self.D_ams)):
                self.D_ams[Each_Template_ams] = aTemplate.D_ams[Each_Template_ams]
                
            for values_Each_Template_ams in list(aTemplate.D_ams[Each_Template_ams]):
                if not (values_Each_Template_ams in list(self.D_ams[Each_Template_ams])):
                    self.D_ams[Each_Template_ams][values_Each_Template_ams] = aTemplate.D_ams[Each_Template_ams][values_Each_Template_ams]
       
        for Each_ams in list(self.D_app):
            if not (Each_ams in list(aTemplate.D_app)):
                del self.D_app[Each_ams]
                break
            
            for values_each_AMS in list(self.D_app[Each_ams]):
                if not (values_each_AMS in list(aTemplate.D_app[Each_ams])):
                    del self.D_app[Each_ams][values_each_AMS]   
                
        for Each_Template_ams in list(aTemplate.D_app):
            if not (Each_Template_ams in list(self.D_app)):
                self.D_app[Each_Template_ams] = aTemplate.D_app[Each_Template_ams]
                
            for values_Each_Template_ams in list(aTemplate.D_app[Each_Template_ams]):
                if not (values_Each_Template_ams in list(self.D_app[Each_Template_ams])):
                    self.D_app[Each_Template_ams][values_Each_Template_ams] = aTemplate.D_app[Each_Template_ams][values_Each_Template_ams]
         
        for Each_ams in list(self.D_content):
            if not (Each_ams in list(aTemplate.D_content)):
                del self.D_content[Each_ams]
              
                
        for Each_Template_ams in list(aTemplate.D_content):
            if not (Each_Template_ams in list(self.D_content)):
                self.D_content[Each_Template_ams] = aTemplate.D_content[Each_Template_ams]
                
        print("DOC GUARDADO: ", "Doc Guardado")
    
    def UpdateXml(self, NuevosValores):

        for eachType in NuevosValores["D_ams"]:
            if self.D_ams.get(eachType):
                for fields in NuevosValores["D_ams"][eachType]:
                    if NuevosValores["D_ams"][eachType][fields] != '' or len(NuevosValores["D_ams"][eachType][fields]) > 0:
                        if fields in self._multiples:
                            self.D_ams[eachType][fields].clear()
                            allfields = re.split(r"(.+)", NuevosValores["D_ams"][eachType][fields])
                            for eachfield in allfields:
                                self.D_ams[eachType][fields].append(eachfield) 
                                   
                        else:
                            self.D_ams[eachType][fields] = NuevosValores["D_ams"][eachType][fields]
                    
        for eachType in NuevosValores["D_app"]:
            if self.D_app.get(eachType):
                for fields in NuevosValores["D_app"][eachType]:
                    if NuevosValores["D_app"][eachType][fields] != '' or len(NuevosValores["D_app"][eachType][fields]) > 0:
                        if fields in self._multiples:
                            try:
                                self.D_app[eachType][fields].clear()
                            except KeyError:
                                print("KeyError: ", "self.D_app[" + eachType + "][" +fields + "] no existe")
                                pass
                            allfields = re.findall(r"(.+)", NuevosValores["D_app"][eachType][fields])
                            for eachfield in allfields:
                                self.D_app[eachType][fields].append(eachfield)
                                
                        else:
                            self.D_app[eachType][fields] = NuevosValores["D_app"][eachType][fields]                            

        for eachType in NuevosValores["D_content"]:
            if self.D_content.get(eachType) and NuevosValores["D_content"][eachType] != '':
                self.D_content[eachType] = NuevosValores["D_content"][eachType]


        return 1
                            
if __name__ == "__main__":
    
    print("Wrong Module: ", "Sorry, you initialize from the wrong module")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    