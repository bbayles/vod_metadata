## Introduction
This project contains a library and tools for manipulating and generating
metadata files that conform to the CableLabs VOD Metada 1.1 specification, which
is described in these two documents:
* [Content Specification](http://cablelabs.com/specification/cablelabs-video-on-demand-content-specification-version-1-1/)
* [Asset Distribution Interface Specification](http://www.cablelabs.com/specification/cablelabs-asset-distribution-interface-specification-version-1-1-2/)

If you're looking at this project you probably have some familiarity with that
specification. The goal of this project is to prevent its users from having to
be _too_ familiar with its endearing quirks. 

## Using the metadata generator
This project contains a script that will generate valid VOD metadata for all the
video files in a directory. This guide (written with Windows users who might
not be familiar with Python) shows how get that script up and running.

First, get the pre-requisites:
* Make sure you've got a recent version of [Python](http://python.org)
 installed. I develop for version 3.4, but will try to support 2.7
* Download the [MediaInfo](http://mediaarea.net/en/MediaInfo) CLI archive and
 extract it somewhere (e.g. to `C:\Program Files\MediaInfo`)
* (Optional) Make sure you've got the [lxml](http://lxml.de) library installed. If you're
 on Windows you can use the installer from
 [Christoph Gohlke's Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

Then, get the module ready:
* Download this module's
 [source archive from Github](http://github.com/bbayles/vod_metadata/zipball/master/)
 and extract it somewhere (e.g. to `C:\temp\vod_metadata-master`)
* Edit `vod_metadata/vod_config.ini` to set custom parameters
* Run `setup.py install` to install the module
    * Open a command prompt to the directory where you extracted the source archive
    * Run the `setup.py` script (e.g. `python setup.py install` or `C:\Python34\python.exe setup.py install`)


Once you're set up, open up a command prompt and switch to a directory with
 video files (e.g. `C:\videos`):

```
C:\Videos>dir /b
11 Pink.mpg
12 Banker.mpg
13 Game.mpg
```

Execute the script with the Python interpreter, using the `-m` switch
 (e.g. `C:\Python34\python.exe -m vod_metadata`):

```
C:\Videos>C:\Python34\python.exe -m vod_metadata
Processing 11 Pink.mpg...
Processing 12 Banker.mpg...
Processing 13 Game.mpg...
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

```python
>>> vod_package.D_ams["title"]["Provider_ID"]
'example.com'
>>> vod_package.D_ams["title"]["Asset_ID"]
'MSOT2014020814473655'
```

Do you need to determine whether the asset package contains a poster? Or do you 
need to remove it?

```python
>>> vod_package.has_poster
True
>>> vod_package.remove_poster()
>>> vod_package.has_poster
False
```

Maybe you suspect that your metadata is describing the wrong file? You can update it to describe the correct one:

```python
>>> vod_package.D_app["preview"]["Content_CheckSum"]
'05b441362eccbde82a98fabcafe071c1',
>>> vod_package.check_files()
>>> vod_package.D_app["preview"]["Content_CheckSum"]
'2680090e51970e67b412af35201b9053'
```

Have an XML file for an asset you need to delete?
```python
>>> vod_package.make_delete()
>>> vod_package.D_ams["package"]["Verb"]
'DELETE'
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
* This library assumes that asset packages always have one `movie` asset element,
zero or more `preview` asset elements, and zero or more `poster` asset elements.
No other types of asset element are supported (even though the spec allows for
others). I may add support for other types in the future.
* This library assumes that if you're generating metadata updates to previously-
delivered packages that you don't want to change the structure of the package.
That is, you don't want to add or remove an asset element (like a `preview` or
`poster`).

The `VodPackage` class is defined in the `vod_metadata.VodPackage` sub-module.
 Import it with:

 `from vod_metadata import VodPackage`.

Parse an existing metadata file by instantiating a VodPackage class:

`vod_package = VodPackage(path_to_xml)`

`VodPackage.__init__(self, xml_path)` parses the file given by the `xml_path`
argument. These attributes are exposed:
* `instance.xml_path` - the path to the XML file.
* `instance.tree` - the XML tree as parsed by lxml.
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
  * `instance.D_app["preview"]` and `instance.D_app["poster"]`. These are optional.
* `instance.has_preview` - `True` if there is a preview element, `False` otherwise.
* `instance.has_poster` - `True` if there is a poster element, `False` otherwise.
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
* `VodPackage.remove_preview()` - deletes the preview element from the asset
 package, if there is one to delete.
* `VodPackage.remove_poster()` - deletes the poster element from the asset
 package, if there is one to delete.
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
 file, `template_values.ini` are not valid.

## Contact the author
I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail [Bo Bayles](bbayles+github@gmail.com) with questions and feature suggestions.
