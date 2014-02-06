import os.path
from vod_metadata.md5_checksum import *
from vod_metadata.media_info import *
from vod_metadata.parse_config import *
from vod_metadata.VodPackage import *

_script_path = os.path.abspath(__file__)
_script_path = os.path.split(_script_path)[0]
config_path = os.path.join(_script_path, "template_values.ini")

(extensions,
 MediaInfo_path,
 product,
 provider_id,
 prefix,
 title_category,
 provider,
 ecn_2009) = parse_config(config_path)