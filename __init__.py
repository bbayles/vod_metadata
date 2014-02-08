import os.path
from vod_metadata.parse_config import *

_script_path = os.path.abspath(__file__)
_script_dir = os.path.split(_script_path)[0]
config_path = os.path.join(_script_dir, "template_values.ini")
template_path = os.path.join(_script_dir, "metadata_template.xml")

(extensions,
 MediaInfo_path,
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

from vod_metadata.md5_checksum import *
from vod_metadata.media_info import *
from vod_metadata.VodPackage import *