# VOD metadata file generator
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See http://github.com/bbayles/vod_metadata for documentation and license

from vod_metadata.config_read import parse_config
from vod_metadata.utils import find_data_file


config_path = find_data_file("template_values.ini")
template_path = find_data_file("metadata_template.xml")

(
    extensions,
    product,
    provider_id,
    prefix,
    title_category,
    provider,
    ecn_2009
) = parse_config(config_path)

# The user determines whether the ECN 2009 parameters are included
param_skip = {"Resolution", "Frame_Rate", "Codec"} if ecn_2009 else set()

# Expose the main VodPackage class
from vod_metadata.vodpackage import VodPackage  # noqa
