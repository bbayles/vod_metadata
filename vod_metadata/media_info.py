import collections
import subprocess
from vod_metadata import MediaInfo_path


class MediaInfoError(Exception):
    pass


def call_MediaInfo(file_name):
    """Returns a dictionary of dictionaries with the output of
       MediaInfo -f file_name"""

    result = subprocess.check_output(
        [MediaInfo_path, "-f", file_name], universal_newlines=True
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


def check_video(file_name):
    """
    Scans the given file with MediaInfo and returns the video and audio codec
    information if all the required parameters were found.
    """
    D = call_MediaInfo(file_name)
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


def check_picture(file_name):
    """
    Scans the given file with MediaInfo and returns the picture
    information if all the required parameters were found.
    """
    D = call_MediaInfo(file_name)
    # Check that the file analyzed was a valid movie
    if (
        ("Image" not in D) or
        ("Width" not in D["Image"]) or
        ("Height" not in D["Image"])
    ):
        raise MediaInfoError("Could not determine all picture paramters")

    return D
