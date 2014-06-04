# VOD metadata file generator - test_metadata sub-module
# Copyright 2014 Bo Bayles (bbayles@gmail.com)
# See README for more information
# See LICENSE for license
from vod_metadata import *
from io import BytesIO
import unittest

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
    _ = file_out.write(ref_package.write_xml())
    _ = file_out.seek(0)
    new_package = VodPackage(file_out)
    self.assertEqual(file_out.getvalue(), new_package.write_xml())
  
  def test_checksum(self):
    test_value = md5_checksum(reference_mp4)
    known_value = "f5f66bd6e6b2ed02153d6fa94787626c"
    self.assertEqual(test_value, known_value)
  
  def test_MediaInfo_video(self):
    D = call_MediaInfo(reference_mp4)
    self.assertEqual(D["General"]["Count of audio streams"], '1')
    self.assertEqual(D["General"]["File size"], '251404')
    self.assertEqual(D["General"]["Overall bit rate"], '274758')
    self.assertEqual(D["Video"]["Format profile"], 'High 4:4:4 Predictive@L3.0')
    self.assertEqual(D["Video"]["Commercial name"], 'AVC')
    self.assertEqual(D["Video"]["Frame rate"], '25.000')
    self.assertEqual(D["Video"]["Height"], '480')
    self.assertEqual(D["Video"]["Scan type"], 'Progressive')

# Reference values
script_path = os.path.abspath(__file__)
script_dir = os.path.split(script_path)[0]
reference_xml = os.path.join(script_dir, "reference.xml")
reference_mp4 = os.path.join(script_dir, "reference.mp4")

ams_package = {'Asset_Class': 'package',
               'Asset_ID': 'TSTP2003010204050001',
               'Asset_Name': 'Metadata test (package)',
               'Creation_Date': '2003-01-02',
               'Description': 'Metadata test (package asset)',
               'Product': 'PRD',
               'Provider': '001',
               'Provider_ID': 'example.com',
               'Version_Major': '1',
               'Version_Minor': '0',}
app_package = {'Metadata_Spec_Version': 'CableLabsVOD1.1',}

ams_title = {'Asset_Class': 'title',
             'Asset_ID': 'TSTT2003010204050001',
             'Asset_Name': 'Metadata test (title)',
             'Creation_Date': '2003-01-02',
             'Description': 'Metadata test (title asset)',
             'Product': 'PRD',
             'Provider': '001',
             'Provider_ID': 'example.com',
             'Version_Major': '1',
             'Version_Minor': '0',}
app_title = {'Billing_ID': '0241B',
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
             'Year': '2003',}

ams_movie = {'Asset_Class': 'movie',
             'Asset_ID': 'TSTM2003010204050001',
             'Asset_Name': 'Metadata test (movie)',
             'Creation_Date': '2003-01-02',
             'Description': 'Metadata test (movie asset)',
             'Product': 'PRD',
             'Provider': '001',
             'Provider_ID': 'example.com',
             'Version_Major': '1',
             'Version_Minor': '0',}
app_movie = {'Audio_Type': 'Stereo',
             'Bit_Rate': '3750',
             'Codec': 'MPEG2',
             'Content_CheckSum': '2680090e51970e67b412af35201b9053',
             'Content_FileSize': '252706816',
             'Frame_Rate': '30',
             'Resolution': '480i',
             'Type': 'movie',}

ams_preview = {'Asset_Class': 'preview',
               'Asset_ID': 'TSTR2003010204050001',
               'Asset_Name': 'Metadata test (preview)',
               'Creation_Date': '2003-01-02',
               'Description': 'Metadata test (preview asset)',
               'Product': 'PRD',
               'Provider': '001',
               'Provider_ID': 'example.com',
               'Version_Major': '1',
               'Version_Minor': '0',}
app_preview = {'Audio_Type': 'Stereo',
               'Bit_Rate': '3750',
               'Codec': 'MPEG2',
               'Content_CheckSum': 'e0b1971fbe52920806190207a3036455',
               'Content_FileSize': '252706816',
               'Frame_Rate': '30',
               'Rating': ['NR'],
               'Resolution': '480i',
               'Run_Time': '00:04:56',
               'Type': 'preview',}

ams_poster = {'Asset_Class': 'poster',
              'Asset_ID': 'TSTI2003010204050001',
              'Asset_Name': 'Metadata test (poster)',
              'Creation_Date': '2003-01-02',
              'Description': 'Metadata test (poster asset)',
              'Product': 'PRD',
              'Provider': '001',
              'Provider_ID': 'example.com',
              'Version_Major': '1',
              'Version_Minor': '0',}
app_poster = {'Content_CheckSum': '410b51e0f900502809a22691537b67e3',
              'Content_FileSize': '252706816',
              'Image_Aspect_Ratio': '320x240',
              'Type': 'poster',}

if __name__ == "__main__":
  unittest.main()