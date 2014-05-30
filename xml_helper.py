# VOD metadata file generator - xml_helper sub-module
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license

# lxml's etree.tostring() function supports a different set of arguments than
# Python's xml.etree.ElementTree.tostring() function. This module calls lxml's
# if it is installed, otherwise it uses Python's.
try:
  from lxml import etree
  lxml = True
except ImportError:
  import xml.etree.ElementTree as etree
  lxml = False

def tobytes(ADI):
  doctype = b'<!DOCTYPE ADI SYSTEM "ADI.DTD">'
  if lxml:
    return etree.tostring(ADI,
                          xml_declaration=True,
                          doctype=doctype,
                          encoding='utf-8',
                          pretty_print=True)
  else:
    declaration = b'<?xml version="1.0" encoding="utf-8"?>'
    elements = etree.tostring(ADI, encoding="utf-8")
    
    return b''.join((declaration, doctype, elements))