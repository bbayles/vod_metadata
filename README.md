[![Build Status](https://travis-ci.org/bbayles/vod_metadata.svg?branch=master)](https://travis-ci.org/bbayles/vod_metadata)
[![Coverage Status](https://coveralls.io/repos/bbayles/vod_metadata/badge.svg?branch=master&service=github)](https://coveralls.io/github/bbayles/vod_metadata?branch=master)

## Introduction
This project contains a library and tools for manipulating and generating
metadata files that conform to the CableLabs VOD Metada 1.1 specification, which
is described in these two documents:
* [Content Specification](http://cablelabs.com/specification/cablelabs-video-on-demand-content-specification-version-1-1/)
* [Asset Distribution Interface Specification](http://www.cablelabs.com/specification/cablelabs-asset-distribution-interface-specification-version-1-1-2/)

## Installation

You will need:
* Python (preferably version 2.7 or 3.4+):
  * Windows users: Download and install Python from [python.org](http://python.org).
  * The GUI only works in 3.4+
* MediaInfo (preferably version 0.7.52+)
  * Windows users: Download the [MediaInfo](http://mediaarea.net/en/MediaInfo) __CLI__ package and extract it somewhere (e.g. to `C:\Program Files\MediaInfo`)
* The `vod_metadata` module from [PyPI](https://pypi.python.org/pypi/vod_metadata)
  * Windows users: Open a command prompt. Then run this command: `C:\Python34\python.exe -m pip install vod_metadata`

## Using the metadata generator


You can use the metadata generator to create XML metadata for video files.
The metadata generator can be used through the graphical interface or the command line.

### Quick start

#### Using the GUI:

To open the graphical interface, and execute the following command, using the `-g` switch:

```
C:\Python35\python.exe vod_metadata -g
```

#### Using the Python interpreter command line:

Start by switching to a directory with some video files (e.g. `cd C:\videos`):
```
C:\Videos>dir /b
11 Pink.mpg
12 Banker.mpg
13 Game.mpg
```

Execute the script with the Python interpreter, using the `-m` switch:

```
C:\Python34\python.exe -m vod_metadata
```

After it runs (it can take a bit for the checksums to be calculated) you should
 have minimal valid metadata files for the videos in the directory:

```
C:\Videos>dir /b
11 Pink.mpg
11 Pink_1442.xml
12 Banker.mpg
12 Banker_2743.xml
13 Game.mpg
13 Game_5056.xml
```

To incorporate a preview and/or poster element for the file `something.mpg`:
* Put a `something_preview.mpg` file in the same directory
* Put a `something_poster.bmp` file in the same directory.
* Put a `something_box_cover.bmp` file in the same directory.

The preview file must have the same extension as the movie file,
and the poster / box cover can have either a .bmp or .jpg extension.

### Command line options

Process videos in a particular directory with the `--video-dir` argument.
```
C:\Videos>C:\Python34\python.exe -m vod_metadata  --video-dir "C:\Somewhere\Videos"
```

Specify a different metadata template (useful for adding custom values) with the `--template-path` argument.
```
C:\Videos>C:\Python34\python.exe -m vod_metadata  --template-path "C:\Somewhere\template.xml"
```

Change what values are used when generating metadata files by specifying the path to a config file ([example](https://github.com/bbayles/vod_metadata/blob/master/vod_metadata/vod_config.ini)):
```
C:\Videos>C:\Python34\python.exe -m vod_metadata  --config-path "C:\Somewhere\config.ini"
```


## Troubleshooting
If you find that you get a `RuntimeError: MediaInfo not found.` error message, you can specify the path to MediaInfo on the command line:

```
C:\Videos>C:\Python34\python.exe -m vod_metadata  --mediainfo-path "C:\Somewhere\MediaInfo.exe"
```

Be sure that you've got the command line version of MediaInfo and not the GUI version.

## Using the library
You can use the module to edit already-existing metadata files.

First, import the module:

```python
>>> from vod_metadata import VodPackage
```

Next, read in an existing metadata file:

```python
>>> vod_package = VodPackage("C:/Videos/The Hounds of Baskerville.xml")
```

You can now read and edit the metadata through Python dictionaries
 (`vod_package.D_ams`, `vod_package.D_app`, `vod_package.D_content`).
 Maybe you need to know the `Provider_ID` and `Asset_ID` for the title
 asset?



Do you need to determine whether the asset package contains a poster? Or do you 
need to remove it?

```python
>>> vod_package.has_poster
True
>>> vod_package.remove_poster()
>>> vod_package.has_poster
False
```

Save your edited file like so:

```python
# Save a new version
>>> s = vod_package.write_xml()
>>> with open("altered.xml", 'wb') as outfile:
...     outfile.write(s)
# Overwrite the original file
>>> vod_package.overwrite_xml()
```

## Library reference

__Note__: This library makes some assumptions about VOD metadata that you might
need to keep in mind:
* Asset packages must have one `movie` asset element.
* Asset packages _may_ have zero or one `preview`, `poster`, or `box cover` asset elements.
* Asset packages may not have any other types of asset element (even though the spec allows for custom ones).
* Metadata updates may not alter the asset elements in the package
 (i.e. the `preview`, `poster`, or `box cover` asset elements cannot be removed).

The `VodPackage` class is defined in the `vod_metadata.VodPackage` sub-module.
 Import it with:

 `from vod_metadata import VodPackage`.

Parse an existing metadata file by instantiating a VodPackage class:

`vod_package = VodPackage(path_to_xml)`

`VodPackage.__init__(self, xml_path)` parses the file given by the `xml_path`
argument. These attributes are exposed:
* `instance.xml_path` - the path to the XML file.
* `instance.tree` - the XML tree as parsed by etree.
* `instance.D_ams` - A dictionary of dictionaries to hold the "AMS"
 attributes. These identify the asset package, title asset, and asset elements.
 See the CableLabs specification for more information. The sub-dictionaries 
 include:
  * `instance.D_ams["package"]`, `instance.D_ams["title"]`, and
 `instance.D_ams["movie"]`. These are required.
  * `instance.D_ams["preview"]` and `instance.D_ams["poster"]`. These are optional.
* `instance.D_app` - A dictionary of dictionaries to hold the "App_Data"
 attributes. These describe the assets identified by the AMS sections. As with the AMS
 data, these sub-dictionaries are included:
  * `instance.D_app["package"]`, `instance.D_app["title"]`, and
 `instance.D_app["movie"]`. These are required.
  * `instance.D_app["preview"]`, `instance.D_app["poster"]`, `instance.D_app["box cover"]`. These are optional.
* `instance.has_preview` - `True` if there is a preview element, `False` otherwise.
* `instance.has_poster` - `True` if there is a poster element, `False` otherwise.
* `instance.has_box_cover` - `True` if there is a box cover element, `False` otherwise.
* `instance.is_update` - `True` if the AMS data for the package indicates that the
 `Version_Major` is something other than `1`, `False` otherwise.
* `instance.is_delete` - `True` if the AMS data for the package has
 `"Verb" = "DELETE"`, `False` otherwise.

The `VodPackage` class exposes these methods:
* `VodPackage.write_xml(rewrite=False)` - Creates a new XML file that
 reflects any edits you've made to the metadata. Returns a `bytes` object that
 can be written to a file.
  * If `rewrite` is `False` then the content files specified by the `Content`
 tags won't be checked for existence or consistency with the supplied metadata.
  * If `rewrite` is True then the content files will be checked with
 `VodPackage.check_files()`.
* `VodPackage.overwrite_xml(rewrite=False)` - Calls `VodPackage.write_xml`,
 optionally with `rewrite`. Saves the result over the original XML file.
* `VodPackage.check_files()` - Calls MediaInfo and sets the following
 attributes (if applicable) for each of the asset elements: `Content_FileSize`,
 `Content_CheckSum`, `Run_Time`, `Display_Run_Time`, `Codec`, `Audio_Type`,
 `Resolution`, `Frame Rate`, and `Bit_Rate`.
* `VodPackage.remove_preview()` - deletes the preview element from the asset package, if there is one to delete.
* `VodPackage.remove_poster()` - deletes the poster element from the asset package, if there is one to delete.
* `VodPackage.remove_box_cover()` - deletes the box cover element from the asset package, if there is one to delete.
* `VodPackage.make_update()` - increments all the `Version_Major` values and
 marks the package as a metadata update. Content tags will not be written when
 using `instance.write_xml()`. See the note above about the assumptions the
 library makes about updates for previously-delivered packages!
* `VodPackage.make_delete()` - sets the `Verb` value to `DELETE` amd marks
 the package as a metadata update.

The `vod_metadata` module exposes these exceptions:
* `MissingElement` - raised if you try to write an asset package without a `movie`
 element, if you use MediaInfo to scan an element that is missing, or if you
 try to remove an element that is not present.
* `InvalidMpeg` - raised if you scan a video file and MediaInfo returns something
 not recognized as valid by the spec. See section 5.3.1 of MD-SP-VOD-CONTENT1.1 .
* `MediaInfoError` - raised if you scan a video or picture file and MediaInfo
  doesn't return all the necessary information.
* `ConfigurationError` - raised if the values specified in the configuration
 file, `vod_config.ini` are not valid.

## Contact the author
I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail [Bo Bayles](bbayles+github@gmail.com) with questions and feature suggestions.
