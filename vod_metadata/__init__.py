# VOD metadata file generator
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See http://github.com/bbayles/vod_metadata for documentation and license

import os.path
import sys
from vod_metadata.config_read import parse_config

# Find data files when frozen. Adapted from cx_Freeze documentation:
# http://cx-freeze.readthedocs.org/en/latest/faq.html
def find_data_file(filename):
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, filename)

config_path = find_data_file("template_values.ini")
template_path = find_data_file("metadata_template.xml")

(extensions,
 product,
 provider_id,
 prefix,
 title_category,
 provider,
 ecn_2009) = parse_config(config_path)

# The user determines whether the ECN 2009 parameters are included
param_skip = set()
if not ecn_2009:
    param_skip.add("Resolution")
    param_skip.add("Frame_Rate")
    param_skip.add("Codec")

# Find MediaInfo
with open(find_data_file("MediaInfo.pth"), mode='r') as _infile:
    for MediaInfo_path in _infile:
        MediaInfo_path = MediaInfo_path.strip()
        if os.path.isfile(MediaInfo_path):
            break
    else:
        raise RuntimeError("MediaInfo not found. Specify the path to MediaInfo in\
          the install directory's MediaInfo.pth file.")

from vod_metadata.md5_calc import *
from vod_metadata.media_info import *
from vod_metadata.vodpackage import *
from vod_metadata.md_gen import *
