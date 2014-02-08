# VOD metadata file generator. When run as a script against a  directory with
# video files will generate XML files for each video file that conform to the
# CableLabs VOD Metadata 1.1 specification
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license
from vod_metadata import *

if __name__ == "__main__":
  generate_metadata()