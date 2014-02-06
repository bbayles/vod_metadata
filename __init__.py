from vod_metadata.md5_checksum import *
from vod_metadata.media_info import *
from vod_metadata.parse_config import *
from vod_metadata.VodPackage import *

(extensions,
 MediaInfo_path,
 product,
 provider_id,
 prefix,
 title_category,
 provider,
 ecn_2009) = parse_config("./template_values.ini")