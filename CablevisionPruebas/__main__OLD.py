from __future__ import print_function

from argparse import ArgumentParser
from io import open
from os import chdir, getcwd, listdir
from os.path import abspath, splitext

from vod_metadata import VodPackage
from vod_metadata.md_gen import generate_metadata
from vod_metadata.config_read import parse_config
from vod_metadata import default_config_path, default_template_path




config_path = default_config_path
vod_config = parse_config(abspath(config_path))

template_path = default_template_path
template_path = abspath(template_path)

for file_path in listdir(getcwd()):
    # Only process movie files (skip previews)
    file_name, file_ext = splitext(file_path)
    if file_ext not in vod_config.extensions:
        continue

    
    vod_package = generate_metadata(file_path, vod_config, template_path)
    
    s = vod_package.write_xml(rewrite=True)
    with open(vod_package.xml_path, "wb") as outfile:
        _ = outfile.write(s)

print("LISTOOOO!!! =D")

