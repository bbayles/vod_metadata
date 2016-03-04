'''
Created on 3 de mar. de 2016

@author: nmastromarino
'''
from __future__ import division
from io import open
from vod_metadata.xml_helper import etree,tobytes

class MissingElement(Exception):
    pass    
    
class MyXML(object):
        
    _multiples = {
            "Provider_Content_Tier", "Subscriber_View_Limit", "Rating",
            "MSORating", "Advisories", "Audience", "Actors", "Director",
            "Producers", "Category", "Genre", "Chapter", "Recording_Artist",
            "Song_Title", "Languages", "Subtitle_Languages", "Dubbed_Languages"
        }
    
    
    def __init__(self, xml_path, vod_config=None):
        
        
        self.xml_path = xml_path
        self.tree = etree.parse(self.xml_path)
            
        self.D_ams = {}
        self.D_app = {}
        self.D_content = {}    
        
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
            if key in self._multiples:
                if key in D:
                    D[key].append(value)
                else:
                    D[key] = [value]
            # Others can only occur once and are treated as plain values
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


                            
if __name__ == "__main__":
    elpath = "C:\\Users\\nmastromarino\\Proyectos Codigo\\VOD_METADATA_GUI\\TestMastrom\\metadata_template.xml"
    elpathD = "C:\\Users\\nmastromarino\\Proyectos Codigo\\VOD_METADATA_GUI\\TestMastrom\\ArchivoFinal.xml"
    ElPathEjemplo = "C:\\Users\\nmastromarino\\Proyectos Codigo\\VOD_METADATA_GUI\\TestMastrom\\Modelo1.xml"
    myXmlInstancia1 = MyXML(elpath)
    myXmlejemplo = MyXML(ElPathEjemplo)
    
    
    myXmlInstancia1.D_ams["package"].update(
        {
            "Provider":  myXmlejemplo.D_ams["package"]["Provider"]
        }
    )
    
    myXmlInstancia1.D_app["title"]["Actors"] = myXmlejemplo.D_app["title"]["Actors"]
    
    
    
    s = myXmlInstancia1.write_xml(rewrite=True)
    with open(elpathD, "wb") as outfile:
        _ = outfile.write(s)
            
            
    print("RESPOSE: ", myXmlInstancia1)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    