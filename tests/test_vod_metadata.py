from copy import deepcopy
from configparser import ConfigParser
from datetime import datetime
from io import BytesIO, open
import unittest
try:
    from unittest.mock import MagicMock, patch
except ImportError:
    from mock import MagicMock, patch
import os.path

from vod_metadata import config_path, find_data_file
from vod_metadata.config_read import ConfigurationError, parse_config
from vod_metadata.md5_calc import md5_checksum
from vod_metadata.md_gen import generate_metadata
from vod_metadata.media_info import (
    call_MediaInfo,
    check_picture,
    check_video,
    find_MediaInfo,
    MediaInfoError,
)
from vod_metadata.vodpackage import MissingElement, VodPackage
from vod_metadata.xml_helper import etree, tobytes


@patch(
    "vod_metadata.config_read.configparser.ConfigParser.read",
    ConfigParser.read_file
)
class ConfigReadTests(unittest.TestCase):
    def setUp(self):
        with open(find_data_file(config_path), mode='r') as infile:
            self.config_lines = [line.strip() for line in infile if line]

    def _modify_key(self, key, value):
        target = "{} = ".format(key)
        commented_target = "# {} = ".format(key)
        if value is None:
            replace_str = ''
        else:
            replace_str = "{} = {}".format(key, value)

        ret = self.config_lines[:]
        for i, line in enumerate(ret):
            if line.startswith(target) or line.startswith(commented_target):
                ret[i] = replace_str
                return ret

    def test_extensions(self):
        # Test default value
        actual = parse_config(self._modify_key("extensions", None))[0]
        expected = {".mpg", ".ts", ".mp4"}
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("extensions", "mpg, mpg")
        actual = parse_config(config_lines)[0]
        expected = {'.mpg'}
        self.assertEqual(actual, expected)

    def test_product(self):
        # Test default value
        config_lines = self._modify_key("product", None)
        actual = parse_config(config_lines)[1]
        expected = "MOD"
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("product", "FOD")
        actual = parse_config(config_lines)[1]
        expected = "FOD"
        self.assertEqual(actual, expected)

        # Test incorrect value
        config_lines = self._modify_key("product", 'x' * 21)
        with self.assertRaises(ConfigurationError):
            parse_config(config_lines)[1]

    def test_provider_id(self):
        # Test default value
        config_lines = self._modify_key("provider_id", None)
        actual = parse_config(config_lines)[2]
        expected = "example.com"
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("provider_id", "EXAMPLE.org")
        actual = parse_config(config_lines)[2]
        expected = "example.org"
        self.assertEqual(actual, expected)

        # Test incorrect values
        incorrect_values = [
            "{}.com".format("x" * 17),  # Too long
            "examplecom",  # Too few dots
            "www.example.com",  # Too many dots
            "example.c",  # The bit after the dot is too short
        ]
        for value in incorrect_values:
            config_lines = self._modify_key("provider_id", value)
            with self.assertRaises(ConfigurationError):
                parse_config(config_lines)[2]

    def test_prefix(self):
        # Test default value
        config_lines = self._modify_key("prefix", None)
        actual = parse_config(config_lines)[3]
        expected = "MSO"
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("prefix", "ABC")
        actual = parse_config(config_lines)[3]
        expected = "ABC"
        self.assertEqual(actual, expected)

        # Test incorrect values
        incorrect_values = [
            "ABCD",  # Too many letters
            "!!!",  # Not alphanumeric
        ]
        for value in incorrect_values:
            config_lines = self._modify_key("prefix", value)
            with self.assertRaises(ConfigurationError):
                parse_config(config_lines)[3]

    def test_category(self):
        # Test default value
        config_lines = self._modify_key("title_category", None)
        actual = parse_config(config_lines)[4]
        expected = "Testing/Videos"
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("title_category", "Testing/HD")
        actual = parse_config(config_lines)[4]
        expected = "Testing/HD"
        self.assertEqual(actual, expected)

        # Test incorrect value
        config_lines = self._modify_key("title_category", 'x' * 21)
        with self.assertRaises(ConfigurationError):
            parse_config(config_lines)[4]

    def test_provider(self):
        # Test default value
        config_lines = self._modify_key("provider", None)
        actual = parse_config(config_lines)[5]
        expected = "001"
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("provider", "002")
        actual = parse_config(config_lines)[5]
        expected = "002"
        self.assertEqual(actual, expected)

        # Test incorrect value
        config_lines = self._modify_key("provider", 'x' * 21)
        with self.assertRaises(ConfigurationError):
            parse_config(config_lines)[5]

    def test_ecn_2009(self):
        # Test default value
        config_lines = self._modify_key("ecn_2009", None)
        actual = parse_config(config_lines)[6]
        expected = False
        self.assertEqual(actual, expected)

        # Test custom value
        config_lines = self._modify_key("ecn_2009", "True")
        actual = parse_config(config_lines)[6]
        expected = True
        self.assertEqual(actual, expected)

    def test_mediainfo_path(self):
        # Test default value
        config_lines = self._modify_key("path", None)
        actual = parse_config(config_lines)[7]
        self.assertIsNone(actual)

        # Test custom value
        config_lines = self._modify_key("path", "/usr/bin/mediainfo")
        actual = parse_config(config_lines)[7]
        expected = "/usr/bin/mediainfo"
        self.assertEqual(actual, expected)

    def test_no_config(self):
        actual = parse_config([])
        expected = (
            {".mpg", ".ts", ".mp4"},
            "MOD",
            "example.com",
            "MSO",
            "Testing/Videos",
            "001",
            False,
            None,
        )
        self.assertEqual(actual, expected)


class Md5CalcTests(unittest.TestCase):
    def test_checksum(self):
        test_value = md5_checksum(reference_mp4)
        known_value = "f5f66bd6e6b2ed02153d6fa94787626c"
        self.assertEqual(test_value, known_value)


class MdGenTests(unittest.TestCase):
    @patch('vod_metadata.md_gen.random', autospec=True)
    @patch('vod_metadata.md_gen.datetime.datetime', autospec=True)
    def setUp(self, mock_datetime, mock_random):
        mock_random.randint.return_value = 1020
        mock_datetime.today.return_value = datetime(1999, 9, 9, 1, 2)
        vod_config = parse_config(find_data_file(config_path))
        vod_config = vod_config._replace(ecn_2009=True)
        self.vod_package = generate_metadata(reference_mp4, vod_config)
        self.ams_expected = {
            "Provider":  "001",
            "Product": "MOD",
            "Version_Major": '1',
            "Version_Minor": '0',
            "Creation_Date": "1999-09-09",
            "Provider_ID": "example.com",
        }

    def test_package(self):
        # XML path
        actual = os.path.split(self.vod_package.xml_path)[1]
        expected = "reference_1020.xml"
        self.assertEqual(actual, expected)

        # Package AMS values
        actual = self.vod_package.D_ams["package"]
        expected = self.ams_expected.copy()
        package_expected = {
            "Asset_Name": "reference 1020 (package)",
            "Description": "reference 1020 (package asset)",
            "Asset_Class": "package",
            "Asset_ID": "MSOP1999090901021020",
        }
        expected.update(package_expected)
        self.assertEqual(actual, expected)

        # Package APP values
        actual = self.vod_package.D_app["package"]
        expected = {"Metadata_Spec_Version": "CableLabsVOD1.1"}
        self.assertEqual(actual, expected)

    def test_title(self):
        # Title AMS values
        actual = self.vod_package.D_ams["title"]
        expected = self.ams_expected.copy()
        title_expected = {
            "Asset_Name": "reference 1020 (title)",
            "Description": "reference 1020 (title asset)",
            "Asset_Class": "title",
            "Asset_ID": "MSOT1999090901021020",
        }
        expected.update(title_expected)
        self.assertEqual(actual, expected)

        # Title APP values
        actual = self.vod_package.D_app["title"]
        expected = {
            "Type": "title",
            "Title_Brief": "reference 1020",
            "Title": "reference 1020",
            "Summary_Short": "reference 1020",
            "Rating": ["NR"],
            "Closed_Captioning": 'N',
            "Year": "1999",
            "Category": ["MSO Lab"],
            "Genre": ["Other"],
            "Show_Type": "Other",
            "Billing_ID": "1020B",
            "Licensing_Window_Start": "1999-09-09",
            "Licensing_Window_End": "2002-06-04",
            "Preview_Period": "300",
            "Provider_QA_Contact": "N/A"
        }
        self.assertEqual(actual, expected)

    def test_movie(self):
        # Movie AMS values
        actual = self.vod_package.D_ams["movie"]
        expected = self.ams_expected.copy()
        movie_expected = {
            "Asset_Name": "reference 1020 (movie)",
            "Description": "reference 1020 (movie asset)",
            "Asset_Class": "movie",
            "Asset_ID": "MSOM1999090901021020",
        }
        expected.update(movie_expected)
        self.assertEqual(actual, expected)

        # Movie APP values
        actual = self.vod_package.D_app["movie"]
        expected = {
            'Audio_Type': 'Stereo',
            'Bit_Rate': '275',
            'Codec': 'AVC HP@L30',
            'Content_CheckSum': 'f5f66bd6e6b2ed02153d6fa94787626c',
            'Content_FileSize': '251404',
            'Frame_Rate': '25',
            'Resolution': '480p',
            'Type': 'movie',
        }
        self.assertEqual(actual, expected)

        # Movie Content values
        actual = self.vod_package.D_content["movie"]
        expected = reference_mp4
        self.assertEqual(actual, expected)


class MediaInfoTests(unittest.TestCase):
    def setUp(self):
        self.D_reference = {
            "General": {
                "Count of audio streams": '1',
                "Count of audio streams": '1',
                "File size": '251404',
                "Overall bit rate": '274758',
            },
            "Video": {
                "Format profile": 'High 4:4:4 Predictive@L3.0',
                "Commercial name": 'AVC',
                "Frame rate": '25.000',
                "Height": '480',
                "Scan type": 'Progressive',
            },
        }

    @patch('vod_metadata.media_info.os.path.isfile', autospec=True)
    def test_find_MediaInfo(self, mock_isfile):
        mock_isfile.return_value = True
        self.assertIsNotNone(find_MediaInfo())

        mock_isfile.return_value = False
        with self.assertRaises(RuntimeError):
            find_MediaInfo()

    def test_call_MediaInfo(self):
        D = call_MediaInfo(reference_mp4)
        for section in self.D_reference.keys():
            for key, expected in self.D_reference[section].items():
                actual = D[section][key]
                self.assertEqual(actual, expected)

    @patch('vod_metadata.media_info.call_MediaInfo', autospec=True)
    def test_check_video(self, mock_call_MediaInfo):
        # No modification -> should return normally
        mock_call_MediaInfo.return_value = self.D_reference
        self.assertEqual(check_video(reference_mp4), self.D_reference)

        # No General or Video section -> should fail
        for key in self.D_reference.keys():
            D = deepcopy(self.D_reference)
            del D[key]
            mock_call_MediaInfo.return_value = D
            with self.assertRaises(MediaInfoError):
                check_video(reference_mp4)

        # Missing keys -> should fail
        for section in ("General", "Video"):
            for key in self.D_reference[section]:
                D = deepcopy(self.D_reference)
                del D[section][key]
                mock_call_MediaInfo.return_value = D
                with self.assertRaises(MediaInfoError):
                    check_video(reference_mp4)

    @patch('vod_metadata.media_info.call_MediaInfo', autospec=True)
    def test_check_picture(self, mock_call_MediaInfo):
        # No modification -> should return normally
        D_image = {"Image": {"Width": "320", "Height": "240"}}
        mock_call_MediaInfo.return_value = D_image
        self.assertEqual(check_picture(None), D_image)

        # Missing keys -> should fail
        for D_image in (
            {}, {"Image": {"Width": "320"}}, {"Image": {"Height": "320"}}
        ):
            mock_call_MediaInfo.return_value = D_image
            with self.assertRaises(MediaInfoError):
                check_picture(None)


class XmlHelperTests(unittest.TestCase):
    def setUp(self):
        self.zero = etree.Element('zero')
        self.one = etree.SubElement(self.zero, 'one')
        self.two = etree.SubElement(self.one, 'two', attrib={'key': 'value'})
        self.expected_lines = [
            b'<?xml version=\'1.0\' encoding=\'utf-8\'?>\n',
            b'<!DOCTYPE ADI SYSTEM "ADI.DTD">\n',
            b'<zero>\n'
            b'  <one>\n'
            b'    <two key="value" />\n'
            b'  </one>\n</zero>\n'
        ]

    def test_tobytes(self):
        actual = tobytes(b'<!DOCTYPE ADI SYSTEM "ADI.DTD">', self.zero)
        expected = b''.join(self.expected_lines)
        self.assertEqual(actual, expected)


class VodMetadataTests(unittest.TestCase):
    def test_dictionaries(self):
        vod_package = VodPackage(reference_xml)
        # Package
        self.assertEqual(vod_package.D_ams["package"], ams_package)
        self.assertEqual(vod_package.D_app["package"], app_package)
        # Title
        self.assertEqual(vod_package.D_ams["title"], ams_title)
        self.assertEqual(vod_package.D_app["title"], app_title)
        # Movie
        self.assertEqual(vod_package.D_ams["movie"], ams_movie)
        self.assertEqual(vod_package.D_app["movie"], app_movie)
        # Preview
        self.assertEqual(vod_package.D_ams["preview"], ams_preview)
        self.assertEqual(vod_package.D_app["preview"], app_preview)
        # Poster
        self.assertEqual(vod_package.D_ams["poster"], ams_poster)
        self.assertEqual(vod_package.D_app["poster"], app_poster)

    def test_roundtrip(self):
        ref_package = VodPackage(reference_xml)
        file_out = BytesIO()
        file_out.write(ref_package.write_xml())
        file_out.seek(0)
        new_package = VodPackage(file_out)
        self.assertEqual(file_out.getvalue(), new_package.write_xml())

    def test_missing_movie(self):
        vod_package = VodPackage(reference_xml)
        del vod_package.D_ams["movie"]
        with self.assertRaises(MissingElement):
            vod_package.write_xml()

    @patch('vod_metadata.vodpackage.VodPackage.check_files', autospec=True)
    def test_rewrite(self, mock_check_file):
        vod_package = VodPackage(reference_xml)
        vod_package.write_xml(rewrite=True)
        mock_check_file.assert_called_once_with(vod_package)

    @patch('vod_metadata.vodpackage.open', autospec=True)
    def test_overwrite_xml(self, mock_open):
        mock_open.return_value = MagicMock()
        file_handle = mock_open.return_value.__enter__.return_value
        vod_package = VodPackage(reference_xml)
        vod_package.overwrite_xml()
        file_handle.write.assert_called_once_with(vod_package.write_xml())


# Reference values
script_path = os.path.abspath(__file__)
script_dir = os.path.split(script_path)[0]
reference_xml = os.path.join(script_dir, "reference.xml")
reference_mp4 = os.path.join(script_dir, "reference.mp4")

ams_package = {
    'Asset_Class': 'package',
    'Asset_ID': 'TSTP2003010204050001',
    'Asset_Name': 'Metadata test (package)',
    'Creation_Date': '2003-01-02',
    'Description': 'Metadata test (package asset)',
    'Product': 'PRD',
    'Provider': '001',
    'Provider_ID': 'example.com',
    'Version_Major': '1',
    'Version_Minor': '0',
}
app_package = {'Metadata_Spec_Version': 'CableLabsVOD1.1'}

ams_title = {
    'Asset_Class': 'title',
    'Asset_ID': 'TSTT2003010204050001',
    'Asset_Name': 'Metadata test (title)',
    'Creation_Date': '2003-01-02',
    'Description': 'Metadata test (title asset)',
    'Product': 'PRD',
    'Provider': '001',
    'Provider_ID': 'example.com',
    'Version_Major': '1',
    'Version_Minor': '0',
}
app_title = {
    'Billing_ID': '0241B',
    'Category': ['Test Category', 'Test Category/Second Level'],
    'Closed_Captioning': 'N',
    'Display_Run_Time': '01:02',
    'Genre': ['Other'],
    'Licensing_Window_End': '2023-01-02T23:59:59',
    'Licensing_Window_Start': '2003-01-02',
    'Preview_Period': '241',
    'Provider_QA_Contact': 'username@example.com',
    'Rating': ['NR'],
    'Run_Time': '01:02:03',
    'Show_Type': 'Other',
    'Summary_Short': 'Test Summary_Short',
    'Title': 'Test Title',
    'Title_Brief': 'Test Title_Brief',
    'Type': 'title',
    'Year': '2003',
}

ams_movie = {
    'Asset_Class': 'movie',
    'Asset_ID': 'TSTM2003010204050001',
    'Asset_Name': 'Metadata test (movie)',
    'Creation_Date': '2003-01-02',
    'Description': 'Metadata test (movie asset)',
    'Product': 'PRD',
    'Provider': '001',
    'Provider_ID': 'example.com',
    'Version_Major': '1',
    'Version_Minor': '0',
}
app_movie = {
    'Audio_Type': 'Stereo',
    'Bit_Rate': '3750',
    'Codec': 'MPEG2',
    'Content_CheckSum': '2680090e51970e67b412af35201b9053',
    'Content_FileSize': '252706816',
    'Frame_Rate': '30',
    'Resolution': '480i',
    'Type': 'movie',
}

ams_preview = {
    'Asset_Class': 'preview',
    'Asset_ID': 'TSTR2003010204050001',
    'Asset_Name': 'Metadata test (preview)',
    'Creation_Date': '2003-01-02',
    'Description': 'Metadata test (preview asset)',
    'Product': 'PRD',
    'Provider': '001',
    'Provider_ID': 'example.com',
    'Version_Major': '1',
    'Version_Minor': '0',
}
app_preview = {
    'Audio_Type': 'Stereo',
    'Bit_Rate': '3750',
    'Codec': 'MPEG2',
    'Content_CheckSum': 'e0b1971fbe52920806190207a3036455',
    'Content_FileSize': '252706816',
    'Frame_Rate': '30',
    'Rating': ['NR'],
    'Resolution': '480i',
    'Run_Time': '00:04:56',
    'Type': 'preview',
}

ams_poster = {
    'Asset_Class': 'poster',
    'Asset_ID': 'TSTI2003010204050001',
    'Asset_Name': 'Metadata test (poster)',
    'Creation_Date': '2003-01-02',
    'Description': 'Metadata test (poster asset)',
    'Product': 'PRD',
    'Provider': '001',
    'Provider_ID': 'example.com',
    'Version_Major': '1',
    'Version_Minor': '0',
}
app_poster = {
    'Content_CheckSum': '410b51e0f900502809a22691537b67e3',
    'Content_FileSize': '252706816',
    'Image_Aspect_Ratio': '320x240',
    'Type': 'poster',
}

if __name__ == "__main__":
    unittest.main()
