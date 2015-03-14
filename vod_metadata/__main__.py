# VOD metadata file generator
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See http://github.com/bbayles/vod_metadata for documentation and license
from __future__ import print_function

from argparse import ArgumentParser
from io import open
from os import getcwd, listdir
from os.path import splitext

from vod_metadata import config_path
from vod_metadata.config_read import parse_config
from vod_metadata.md_gen import generate_metadata


# Accept arguments from the command line
parser = ArgumentParser()
parser.add_argument(
    '--mediainfo-path', help='Specify the path to the MediaInfo executable'
)
args = parser.parse_args()

if __name__ == "__main__":
    # Retrieve the user's configuration, overriding with command line arguments
    vod_config = parse_config(config_path)
    if args.mediainfo_path is not None:
        vod_config = vod_config._replace(mediainfo_path=args.mediainfo_path)

    for file_path in listdir(getcwd()):
        # Only process movie files
        file_name, file_ext = splitext(file_path)
        if file_ext not in vod_config.extensions:
            continue

        # Create the VodPackage instace
        print("Processing {}...".format(file_path))
        vod_package = generate_metadata(file_path, vod_config)

        # Write the result
        s = vod_package.write_xml(rewrite=True)
        with open(vod_package.xml_path, "wb") as outfile:
            _ = outfile.write(s)
