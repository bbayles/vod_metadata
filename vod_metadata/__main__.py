# VOD metadata file generator
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See http://github.com/bbayles/vod_metadata for documentation and license
from __future__ import print_function

from argparse import ArgumentParser
from io import open
from os import chdir, getcwd, listdir
from os.path import abspath, splitext

from vod_metadata import default_config_path, default_template_path
from vod_metadata.config_read import parse_config
from vod_metadata.md_gen import generate_metadata

from vod_metadata.GUI.XML_Modifier import MyFrame
from tkinter import *

# Accept arguments from the command line
parser = ArgumentParser()
parser.add_argument(
    '--video-dir', help='Specify the path to a directory of videos to process'
)
parser.add_argument(
    '--mediainfo-path', help='Specify the path to the MediaInfo executable'
)
parser.add_argument(
    '--template-path', help='Specify the path to the metadata template'
)
parser.add_argument(
    '--config-path', help='Specify the path to the configuration file'
)
parser.add_argument("-g", "--GUI", help="Show a nice GUI",
                    action="store_true")
args = parser.parse_args()

if __name__ == "__main__":
    
    
    if args.GUI:
        root = Tk()
        main = MyFrame(root)
        main.pack(fill="both", expand=True)
        root.mainloop()
    else:    
            
        # Retrieve the user's configuration, overriding with command line arguments
        config_path = args.config_path or default_config_path
        vod_config = parse_config(abspath(config_path))
    
        if args.mediainfo_path is not None:
            vod_config = vod_config._replace(mediainfo_path=args.mediainfo_path)
    
        template_path = args.template_path or default_template_path
        template_path = abspath(template_path)
    
        # If a directory was specified, switch to it
        if args.video_dir is not None:
            chdir(args.video_dir)
    
        for file_path in listdir(getcwd()):
            # Only process movie files (skip previews)
            file_name, file_ext = splitext(file_path)
            if file_ext not in vod_config.extensions:
                continue
            if file_name.endswith('_preview'):
                continue
    
            # Create the VodPackage instace
            print("Processing {}...".format(file_path))
            vod_package = generate_metadata(file_path, vod_config, template_path)
    
            # Write the result
            s = vod_package.write_xml(rewrite=True)
            with open(vod_package.xml_path, "wb") as outfile:
                _ = outfile.write(s)
