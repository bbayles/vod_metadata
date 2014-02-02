# VOD metadata file generator. When run in a directory with video files will
# generate XML files for each video file that conform to the CableLabs VOD
# Metadata 1.1 specification
# Copyright 2013 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license
from media_info import media_info, MediaInfoError
from md5_checksum import md5_checksum
from parse_config import parse_config
import datetime
import os
import random

if __name__ == "__main__":
  # Determine the path to the metadata template and configuration file
  script_path = os.path.abspath( __file__ )
  script_path = os.path.split(script_path)[0]
  config_path = os.path.join(script_path, "template_values.ini")
  infile_path = os.path.join(script_path, "metadata_template.xml")
  
  # Read the values supplied by the user
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
    param_skip.add("%movie_resolution%")
    param_skip.add("%movie_frame_rate%")
    param_skip.add("%movie_codec%")
  
  # The main loop - runs through movie file
  for file_path in os.listdir():
    # Only process movie files
    file_name, file_ext = os.path.splitext(file_path)
    if file_ext not in extensions:
      continue
    print("Processing {}...".format(file_path))
        
    # Time-sensitive values
    timestamp = datetime.datetime.today()
    creation_date = timestamp.strftime("%Y-%m-%d")
    end_date = (timestamp + datetime.timedelta(days=999)).strftime("%Y-%m-%d")
    asset_id = timestamp.strftime("%Y%m%d%H%M")
    
    # Randomly-generated values
    suffix = format(random.randint(0, 9999), "04")
    title_billing_id = "{}B".format(suffix)

    # Video file-specific value
    try:
      mpeg_info = media_info(file_path, MediaInfo_path)
    except MediaInfoError:
      print("Could not analyze {}. Is it a video file?".format(file_path))
      continue
    duration_s = round(float(mpeg_info["General"]["Duration"]) / 1000)
    duration_h, duration_s = divmod(duration_s, 3600)
    duration_m, duration_s = divmod(duration_s, 60)
    duration_h = format(duration_h, "02")
    duration_m = format(duration_m, "02")
    duration_s = format(duration_s, "02")
    commercial_name = mpeg_info["Video"]["Commercial name"]
    format_profile = mpeg_info["Video"]["Format profile"]
    if commercial_name == "MPEG-2 Video":
      movie_codec = "MPEG2"
    elif commercial_name == "AVC":
      avc_profile = format_profile[0]
      avc_level = format_profile[format_profile.find("@"):].replace(".", "")
      movie_codec = "AVC {}P{}".format(avc_profile, avc_level)
    else:
      print("The specification requires MPEG-2 or AVC, but {} is {}".format(file_path, commercial_name))
      continue
    
    # Package section
    package_asset_name = "{} (package)".format(file_name[:20])
    package_description = "{} (package asset)".format(file_name[:20])
    package_asset_id = "{}P{}{}".format(prefix, asset_id, suffix)
    
    # Title section
    title_asset_name = "{} (title)".format(file_name[:20])
    title_description = "{} (title asset)".format(file_name[:20])
    title_asset_id = "{}T{}{}".format(prefix, asset_id, suffix)
    title_title_brief = "{}{}".format(file_name[:15], suffix)
    title_title = "{}{}".format(file_name[:124], suffix)
    run_time = "{}:{}:{}".format(duration_h, duration_m, duration_s)
    display_run_time = "{}:{}".format(duration_h, duration_m)
    
    # Movie section
    movie_asset_name = "{} (movie)".format(file_name[:20])
    movie_description = "{} (movie asset)".format(file_name[:20])
    movie_asset_id = "{}M{}{}".format(prefix, asset_id, suffix)
    movie_audio_type = int(mpeg_info["Audio"].get("Channel(s)", 0))
    movie_audio_type = "Stereo" if  movie_audio_type > 1 else "Mono"
    movie_resolution_height = mpeg_info["Video"]["Height"]
    move_resolution_scan = mpeg_info["Video"]["Scan type"][0].lower()
    movie_resolution = movie_resolution_height + move_resolution_scan
    movie_frame_rate = str(round(float(mpeg_info["Video"]["Frame rate"])))
    movie_bit_rate = str(round(float(mpeg_info["Video"]["Bit rate"]) / 1000))
    
    # Replace the template values with the computed values  
    D = {"%package_provider%": provider,
         "%package_product%": product,
         "%package_asset_name%": package_asset_name,
         "%package_version_major%": "1",
         "%package_version_minor%": "0",
         "%package_description%": package_description,
         "%package_creation_date%": creation_date,
         "%package_provider_id%": provider_id,
         "%package_asset_id%": package_asset_id,
         "%title_provider%": provider,
         "%title_product%": product,
         "%title_asset_name%": title_asset_name,
         "%title_version_major%": "1",
         "%title_version_minor%": "0",
         "%title_description%": title_description,
         "%title_creation_date%": creation_date,
         "%title_provider_id%": provider_id,
         "%title_asset_id%": title_asset_id,
         "%title_title_brief%": title_title_brief,
         "%title_title%": title_title,
         "%title_summary_short%": file_name,
         "%title_rating%": "NR",
         "%title_closed_captioning%": "N",
         "%title_run_time%": run_time,
         "%title_display_run_time%": display_run_time,
         "%title_year%": timestamp.strftime("%Y"),
         "%title_category%": title_category,
         "%title_genre%": "Other",
         "%title_show_type%": "Other",
         "%title_billing_id%": title_billing_id,
         "%title_licensing_window_start%": creation_date,
         "%title_licensing_window_end%": end_date,
         "%title_preview_period%": "300",
         "%title_provider_qa_contact%": "N/A",
         "%movie_provider%": provider,
         "%movie_product%": product,
         "%movie_asset_name%": movie_asset_name,
         "%movie_version_major%": "1",
         "%movie_version_minor%": "0",
         "%movie_description%": movie_description,
         "%movie_creation_date%": creation_date,
         "%movie_provider_id%": provider_id,
         "%movie_asset_id%": movie_asset_id,
         "%movie_audio_type%": movie_audio_type,
         "%movie_resolution%": movie_resolution,
         "%movie_frame_rate%": movie_frame_rate,
         "%movie_codec%": movie_codec,
         "%movie_bit_rate%": movie_bit_rate,
         "%movie_content_filesize%": mpeg_info["General"]["File size"],
         "%movie_content_checksum%": md5_checksum(file_path),
         "%movie_file_name%": file_path}
    
    outfile_path = ''.join((file_name, '_', suffix, ".xml"))
    with open(infile_path, 'r') as infile, open(outfile_path, 'w') as outfile:
      for line in infile:
        if line.count("%") == 2:
          param = ''.join(("%", line.split("%")[1], "%"))
          if (param not in param_skip):
            print(line.replace(param, D[param]), end='', file=outfile)
        else:
          print(line, end='', file=outfile)