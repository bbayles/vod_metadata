import xml.etree.ElementTree as etree


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
    declaration = b"<?xml version='1.0' encoding='UTF-8'?>"
    indent(root_elem)
    elements = etree.tostring(root_elem, encoding="UTF-8")

    return b'\n'.join((declaration, doctype, elements))
