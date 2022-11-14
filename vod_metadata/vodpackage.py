from __future__ import division
from io import open
import os.path
import warnings

from vod_metadata import default_config_path
from vod_metadata.config_read import parse_config
from vod_metadata.md5_calc import md5_checksum
from vod_metadata.media_info import check_video, check_picture
from vod_metadata.xml_helper import etree, tobytes
from vod_metadata.type_validation import validate_D_app, validate_D_ams

__all__ = ["MissingElement", "InvalidMpeg", "VodPackage"]


class MissingElement(Exception):
    pass


class InvalidMpeg(Exception):
    pass


class VodPackage(object):

    # Some metadata attributes can appear more than once in the App_Data
    # sections.
    # TODO: Audio_Type is one of these, but this is not implemented yet
    _multiples = {
        "Provider_Content_Tier", "Subscriber_View_Limit", "Rating",
        "MSORating", "Advisories", "Audience", "Actors", "Director",
        "Producers", "Category", "Genre", "Chapter", "Recording_Artist",
        "Song_Title", "Languages", "Subtitle_Languages", "Dubbed_Languages"
    }

    def __init__(self, xml_path, vod_config=None, validate_type=False):
        self.validate_type = validate_type
        # Retrieve configuration if it's not set already
        if vod_config is None:
            self.vod_config = parse_config(default_config_path)
        else:
            self.vod_config = vod_config

        # The ECN 2009 options are not always supported - check configuration
        # to see whether they should be added.
        if self.vod_config.ecn_2009:
            self.param_skip = set()
        else:
            self.param_skip = {"Resolution", "Frame_Rate", "Codec"}

        self.xml_path = xml_path
        self._get_namespaces()
        self.tree = etree.parse(self.xml_path)

        # The CableLabs VOD Metadata 1.1 specification stores metadata in "AMS"
        # and "App_Data" tags. The files that are part of the package are
        # stored in "Content" tags.
        self.D_ams = {}
        self.D_app = {}
        self.D_content = {}

        ADI = self.tree.getroot()
        self._read_package(ADI)
        self._read_title(ADI)
        self._read_elements(ADI)

        if self.D_ams:
            self.has_preview = "preview" in self.D_ams
            self.has_poster = "poster" in self.D_ams
            self.has_image = "image" in self.D_ams
            self.has_box_cover = "box cover" in self.D_ams
            self.is_delete = self.D_ams.get("Verb", '') == "DELETE"
            self.is_update = self.D_ams["package"]["Version_Major"] != "1"

        if self.validate_type:
            self.D_ams_orig = self.D_ams.copy()
            self.D_app_orig = self.D_app.copy()
            self.D_ams = validate_D_ams(self.D_ams)
            self.D_app = validate_D_app(self.D_app)

    def adi_compatibility(func):
        def wrap(self, *args, **kwargs):
            if len(self.namespaces) <= 1:
                return func(self, *args, **kwargs)
            else:
                return None
        return wrap

    def _get_namespaces(self):
        self.namespaces = dict([node for _, node in etree.iterparse(self.xml_path, events=['start-ns'])])
        if len(self.namespaces) == 1:
            _adi_ns = [*self.namespaces][0]
            etree.register_namespace("", self.namespaces[_adi_ns])
        elif len(self.namespaces) > 1:
            warnings.warn(f'Warning: ADI incompatible, multiple namespaces: {self.namespaces}')

    @adi_compatibility
    def _read_package(self, ADI):
        package_Metadata = ADI.find("Metadata", self.namespaces)
        self.D_ams["package"] = package_Metadata.find("AMS", self.namespaces).attrib
        self.D_app["package"] = self._parse_App_Data(package_Metadata)

    @adi_compatibility
    def _read_title(self, ADI):
        title_Metadata = ADI.find("Asset", self.namespaces).find("Metadata", self.namespaces)
        self.D_ams["title"] = title_Metadata.find("AMS", self.namespaces).attrib
        self.D_app["title"] = self._parse_App_Data(title_Metadata)

    @adi_compatibility
    def _read_elements(self, ADI):
        # Asset elements section: "movie", "preview", "poster", and
        # "box cover" are allowed.
        for ae_Asset in ADI.find("Asset", self.namespaces).findall("Asset", self.namespaces):
            ae_Metadata = ae_Asset.find("Metadata", self.namespaces)
            ae_AMS = ae_Metadata.find("AMS", self.namespaces)
            ae_type = ae_AMS.attrib["Asset_Class"]
            self.D_ams[ae_type] = ae_AMS.attrib
            self.D_app[ae_type] = self._parse_App_Data(ae_Metadata)
            if ae_Asset.find("Content", self.namespaces) is not None:
                self.D_content[ae_type] = (
                    ae_Asset.find("Content", self.namespaces).attrib["Value"]
                )

    @adi_compatibility
    def _parse_App_Data(self, ae_Metadata):
        D = {}
        for App_Data in ae_Metadata.findall("App_Data", self.namespaces):
            key = App_Data.attrib["Name"]
            value = App_Data.attrib["Value"]
            # Some App_Data fields can occur more than once and are treated as
            # a list
            if key in self._multiples:
                if key in D:
                    D[key].append(value)
                else:
                    D[key] = [value]
            # Others can only occur once and are treated as plain values
            else:
                D[key] = value
        return D

    @adi_compatibility
    def _write_App_Data(self, ae_type, parent_Metadata):
        for key, value in sorted(
            self.D_app[ae_type].items(), key=lambda x: x[0]
        ):
            # Configuration controls whether certain values get skipped
            if key in self.param_skip:
                continue
            # Some of the App_Data tags can be repeated
            if key in self._multiples:
                for v in value:
                    ae_App_Data = etree.SubElement(parent_Metadata, "App_Data")
                    ae_App_Data.set("App", self.D_ams["package"]["Product"])
                    ae_App_Data.set("Name", key)
                    ae_App_Data.set("Value", v)
            # Others are only allowed to appear once
            else:
                ae_App_Data = etree.SubElement(parent_Metadata, "App_Data")
                ae_App_Data.set("App", self.D_ams["package"]["Product"])
                ae_App_Data.set("Name", key)
                ae_App_Data.set("Value", value)

    @adi_compatibility
    def write_xml(self, rewrite=False):
        # A movie element is required by this library
        if "movie" not in self.D_ams:
            raise MissingElement("Package does not specify a movie element")

        # Over-write the given XML values with the ones determined by scanning
        # the video if needed
        if rewrite:
            self.check_files()

        # Root element
        doctype = b'<!DOCTYPE ADI SYSTEM "ADI.DTD">'
        ADI = etree.Element("ADI")

        # Package asset
        package_Metadata = etree.SubElement(ADI, "Metadata")
        package_AMS = etree.SubElement(package_Metadata, "AMS")
        for key, value in sorted(
            self.D_ams["package"].items(), key=lambda x: x[0]
        ):
            package_AMS.set(key, value)
        self._write_App_Data("package", package_Metadata)

        # Title asset
        title_Asset = etree.SubElement(ADI, "Asset")
        title_Metadata = etree.SubElement(title_Asset, "Metadata")
        title_AMS = etree.SubElement(title_Metadata, "AMS")
        for key, value in sorted(
            self.D_ams["title"].items(), key=lambda x: x[0]
        ):
            title_AMS.set(key, value)
        self._write_App_Data("title", title_Metadata)

        # Asset elements
        for ae_type in ("movie", "preview", "poster", "box cover", "image"):
            if ae_type not in self.D_ams:
                continue
            ae_Asset = etree.SubElement(title_Asset, "Asset")
            ae_Metadata = etree.SubElement(ae_Asset, "Metadata")
            # AMS section
            ae_AMS = etree.SubElement(ae_Metadata, "AMS")
            for key, value in sorted(
                self.D_ams[ae_type].items(), key=lambda x: x[0]
            ):
                ae_AMS.set(key, value)
            self._write_App_Data(ae_type, ae_Metadata)
            # Content element, if it is present
            if ae_type in self.D_content:
                ae_Content = etree.SubElement(ae_Asset, "Content")
                ae_Content.set("Value", self.D_content[ae_type])

        return tobytes(doctype, ADI)

    @adi_compatibility
    def overwrite_xml(self, rewrite=False):
        s = self.write_xml(rewrite)
        with open(self.xml_path, mode="wb") as outfile:
            outfile.write(s)

    @adi_compatibility
    def files_present(self):
        # Check the referenced content files for existence. If they are all
        # present return True. Otherwise return False.
        for ae_type, ae_name in self.D_content.items():
            ae_dir = os.path.split(self.xml_path)[0]
            ae_path = os.path.join(ae_dir, ae_name)
            if not os.path.isfile(ae_path):
                return False
        return True

    @adi_compatibility
    def check_files(self):
        for ae_type, ae_name in self.D_content.items():
            # Check to make sure the referenced files exist in the same
            # directory as the XML file
            ae_dir = os.path.split(self.xml_path)[0]
            ae_path = os.path.join(ae_dir, ae_name)
            if not os.path.isfile(ae_path):
                msg = "Package's {} element is missing - {}"
                raise MissingElement(msg.format(ae_type, ae_path))
            # Set the file size and checksum values
            self.D_app[ae_type]["Content_FileSize"] = str(
                os.path.getsize(ae_path)
            )
            self.D_app[ae_type]["Content_CheckSum"] = md5_checksum(ae_path)
            # Use MediaInfo to determine the correct information about the
            # content files
            if (ae_type == "poster") or (ae_type == "box cover") or (ae_type == "image"):
                self._scan_image(ae_type, ae_path)
            else:
                self._scan_video(ae_type, ae_path)

    @adi_compatibility
    def _remove_ae(self, ae_type):
        try:
            del self.D_ams[ae_type]
            del self.D_app[ae_type]
            del self.D_content[ae_type]
        except KeyError:
            msg = "Package does not content a {} element"
            raise MissingElement(msg.format(ae_type))

    @adi_compatibility
    def remove_preview(self):
        self._remove_ae("preview")
        self.has_preview = False

    @adi_compatibility
    def remove_poster(self):
        self._remove_ae("poster")
        self.has_poster = False

    @adi_compatibility
    def remove_box_cover(self):
        self._remove_ae("box cover")
        self.has_box_cover = False

    @adi_compatibility
    def remove_image(self):
        self._remove_ae("image")
        self.has_image = False
        
    @adi_compatibility
    def make_update(self):
        for ae_type in self.D_ams:
            new_version = int(self.D_ams[ae_type]["Version_Major"]) + 1
            self.D_ams[ae_type]["Version_Major"] = str(new_version)
        # The Content element shouldn't be present for updates, per section 8.1
        # of the ADI spec.
        self.D_content = {}
        self.is_update = True

    @adi_compatibility
    def make_delete(self):
        for ae_type in self.D_ams:
            self.D_ams[ae_type]["Verb"] = "DELETE"

        self.is_delete = True

    @adi_compatibility
    def _scan_video(self, ae_type, ae_path):
        mpeg_info = check_video(ae_path, self.vod_config.mediainfo_path)

        # Calculate the run time of the video
        duration_s = int(round(float(mpeg_info["General"]["Duration"]) / 1000))
        duration_h, duration_s = divmod(duration_s, 3600)
        duration_m, duration_s = divmod(duration_s, 60)
        duration_h = format(duration_h, "02")
        duration_m = format(duration_m, "02")
        duration_s = format(duration_s, "02")
        # For the movie asset, the Run_Time and Display_Run_Time are given as
        # part of the title's metadata. For the preview asset, the Run_Time is
        # given as part of the preview's metadata
        if ae_type == "movie":
            self.D_app["title"]["Run_Time"] = "{}:{}:{}".format(
                duration_h, duration_m, duration_s
            )
            self.D_app["title"]["Display_Run_Time"] = "{}:{}".format(
                duration_h, duration_m
            )
        elif ae_type == "preview":
            self.D_app["preview"]["Run_Time"] = "{}:{}:{}".format(
                duration_h, duration_m, duration_s
            )

        # Determine the audio type
        audio_type = int(mpeg_info["Audio"].get("Channel(s)", 0))
        self.D_app[ae_type]["Audio_Type"] = (
            "Stereo" if (audio_type > 1) else "Mono"
        )

        if self.vod_config.ecn_2009:
            # Determine the movie's codec
            commercial_name = mpeg_info["Video"]["Commercial name"]
            format_profile = mpeg_info["Video"]["Format profile"]
            if commercial_name == "MPEG-2 Video":
                self.D_app[ae_type]["Codec"] = "MPEG2"
            elif commercial_name == "AVC":
                avc_profile = format_profile[0]
                avc_level = format_profile.split('@')[1][1:]
                avc_level = format(float(avc_level), '0.1f').replace('.', '')
                codec = "AVC {}P@L{}".format(avc_profile, avc_level)
                self.D_app[ae_type]["Codec"] = codec
            else:
                raise InvalidMpeg("Could not determine codec for {}".format(
                    self.D_content[ae_type])
                )

            # Determine the geometry
            movie_resolution_height = mpeg_info["Video"]["Height"]
            move_resolution_scan = mpeg_info["Video"]["Scan type"][0].lower()
            self.D_app[ae_type]["Resolution"] = "{}{}".format(
                movie_resolution_height, move_resolution_scan
            )

            # Determine the movie's frame rate
            frame_rate = float(mpeg_info["Video"]["Frame rate"])
            self.D_app[ae_type]["Frame_Rate"] = format(frame_rate, '.0f')

        # Determine the movie's bitrate (actually kilobit rate)
        bit_rate = float(mpeg_info["General"]["Overall bit rate"]) / 1000
        self.D_app[ae_type]["Bit_Rate"] = format(bit_rate, '.0f')

    @adi_compatibility
    def _scan_image(self, ae_type, ae_path):
        img_info = check_picture(ae_path, self.vod_config.mediainfo_path)
        img_width = img_info["Image"]["Width"]
        img_height = img_info["Image"]["Height"]
        self.D_app[ae_type]["Image_Aspect_Ratio"] = "{}x{}".format(
            img_width, img_height
        )
