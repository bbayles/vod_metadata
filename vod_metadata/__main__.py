# VOD metadata file generator. When run as a script against a  directory with
# video files will generate XML files for each video file that conform to the
# CableLabs VOD Metadata 1.1 specification
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license
from __future__ import print_function
from io import open
from vod_metadata import *

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
