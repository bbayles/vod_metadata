# VOD metadata file generator
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See http://github.com/bbayles/vod_metadata for documentation and license
from __future__ import print_function

from io import open
import os

from vod_metadata import extensions
from vod_metadata.md_gen import generate_metadata


if __name__ == "__main__":
    for file_path in os.listdir():
        # Only process movie files
        file_name, file_ext = os.path.splitext(file_path)
        if file_ext not in extensions:
            continue
        # Create the VodPackage instace
        print("Processing {}...".format(file_path))
        vod_package = generate_metadata(file_path)
        # Write the result
        s = vod_package.write_xml(rewrite=True)
        with open(vod_package.xml_path, "wb") as outfile:
            _ = outfile.write(s)
