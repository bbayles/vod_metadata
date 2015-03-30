# lxml's etree.tostring() function supports a different set of arguments than
# Python's xml.etree.ElementTree.tostring() function. This module calls lxml's
# if it is installed, otherwise it uses Python's.
try:
    from lxml import etree
    lxml = True
except ImportError:
    import xml.etree.ElementTree as etree
    lxml = False


# Taken from Fredrik Lundh's effbot.org:
# http://effbot.org/zone/element-lib.htm#prettyprint
def indent(elem, level=0):
    i = "\n" + (level * "  ")
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def tobytes(doctype, root_elem):
    if lxml:
        return etree.tostring(
            root_elem,
            xml_declaration=True,
            doctype=doctype,
            encoding='utf-8',
            pretty_print=True
        )
    else:
        declaration = b"<?xml version='1.0' encoding='utf-8'?>"
        indent(root_elem)
        elements = etree.tostring(root_elem, encoding="utf-8")

        return b'\n'.join((declaration, doctype, elements))
