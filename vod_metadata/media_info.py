import collections
import os
import subprocess

from vod_metadata.utils import find_data_file


class MediaInfoError(Exception):
    pass


def find_MediaInfo():
    # Find MediaInfo
    with open(find_data_file("MediaInfo.pth"), mode='r') as _infile:
        for MediaInfo_path in _infile:
            MediaInfo_path = MediaInfo_path.strip()
            if os.path.isfile(MediaInfo_path):
                return MediaInfo_path
        else:
            raise RuntimeError(
                "MediaInfo not found. Specify the path to MediaInfo in the "
                "install directory's MediaInfo.pth file."
            )


def call_MediaInfo(file_name, mediainfo_path=None):
    """Returns a dictionary of dictionaries with the output of
       MediaInfo -f file_name"""
    if mediainfo_path is None:
        mediainfo_path = find_MediaInfo()

    result = subprocess.check_output(
        [mediainfo_path, "-f", file_name], universal_newlines=True
    )
    D = collections.defaultdict(dict)
    for line in result.splitlines():
        line = line.split(':', 1)
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


def check_video(file_name, mediainfo_path=None):
    """
    Scans the given file with MediaInfo and returns the video and audio codec
    information if all the required parameters were found.
    """
    D = call_MediaInfo(file_name, mediainfo_path)
    err_msg = "Could not determine all video paramters"

    if ("General" not in D) or ("Video" not in D):
        raise MediaInfoError(err_msg)

    general_keys = ("Count of audio streams", "File size", "Overall bit rate")
    if any(k not in D["General"] for k in general_keys):
        raise MediaInfoError(err_msg)

    video_keys = (
        "Format profile",
        "Commercial name",
        "Frame rate",
        "Height",
        "Scan type",
    )
    if any(k not in D["Video"] for k in video_keys):
        raise MediaInfoError(err_msg)

    return D


def check_picture(file_name, mediainfo_path=None):
    """
    Scans the given file with MediaInfo and returns the picture
    information if all the required parameters were found.
    """
    D = call_MediaInfo(file_name, mediainfo_path)
    # Check that the file analyzed was a valid movie
    if (
        ("Image" not in D) or
        ("Width" not in D["Image"]) or
        ("Height" not in D["Image"])
    ):
        raise MediaInfoError("Could not determine all picture paramters")

    return D
