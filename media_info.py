# VOD metadata file generator - media_info sub-module
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license
import collections
import subprocess
from vod_metadata import MediaInfo_path

class MediaInfoError(Exception):
  pass

def media_info(file_name):
  """Returns a dictionary of dictionaries with the output of
     MediaInfo -f file_name"""
  
  result = subprocess.check_output([MediaInfo_path,
                                   "-f",
                                   file_name],
                                   universal_newlines=True)
  D = collections.defaultdict(dict)
  for line in result.splitlines():
    line = line.split(':')
    # Skip separators
    if line[0] == '':
      continue
    # Start a new section
    elif len(line) == 1:
      section = line[0].strip()
    # Record section key, value pairs
    else:
      k = line[0].strip()
      v = line[1].strip()
      if k not in D[section]:
        D[section][k] = v
          
  return D

def check_video(file_name):
  """Scans the given file with MediaInfo and returns the video and audio codec
     information if all the required parameters were found."""
  D = media_info(file_name)
  # Check that the file analyzed was a valid movie
  if ("General" not in D
      or "Audio" not in D
      or "Video" not in D
      or "File size" not in D["General"]
      or "Bit rate" not in D["Video"]
      or "Codec profile" not in D["Video"]
      or "Commercial name" not in D["Video"]
      or "Frame rate" not in D["Video"]
      or "Height" not in D["Video"]
      or "Scan type" not in D["Video"]):
    raise MediaInfoError("Could not determine all video paramters")
  
  return D

def check_picture(file_name):
  """Scans the given file with MediaInfo and returns the pictures
     information if all the required parameters were found."""
  D = media_info(file_name)
  # Check that the file analyzed was a valid movie
  if ("Image" not in D
      or "Width" not in D["Image"]
      or "Height" not in D["Image"]):
    raise MediaInfoError("Could not determine all video paramters")
  
  return D