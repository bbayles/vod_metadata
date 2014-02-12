## Introduction
This project contains a library for manipulating and generating metadata files
that conform to the [CableLabs VOD Metada 1.1 specification](http://cablelabs.com/specification/cablelabs-video-on-demand-content-specification-version-1-1/).

## Using the metadata generator
This project contains a script that will generate valid VOD metadata for all the
video files in a directory. This guide (written with Windows users who might
not be familiar with Python) shows how get that script up and running.

First, get the pre-requisites:
* Make sure you've got a recent version of [Python 3](http://python.org)
 installed. Versions 3.2 and up should work.
* Make sure you've got the [lxml](http://lxml.de) library installed. If you're
 on Windows you can use the installer from
 [Christoph Gohlke's Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)
* Download the [MediaInfo](http://mediaarea.net/en/MediaInfo) CLI archive and
 extract it somewhere (e.g. to `C:\Program Files\MediaInfo`).

Then, get the module ready:
* Download this module's
 [source archive from Github](http://github.com/bbayles/vod_metadata/zipball/master/).
 Then extract it to Python's `site-packages` directory (you should wind up with
 the files in e.g. `C:\Python33\lib\site-packages\vod_metadata`).
* Edit `template_values.ini` and set the path to the MediaInfo CLI executable
 and any custom parameters.

Once you're set up, open up a command prompt and switch to a directory with
 video files (e.g. `C:\videos`):

```
C:\Videos>dir /b
11 Pink.mpg
12 Banker.mpg
13 Game.mpg
```

Execute the script with the Python interpreter, using the `-m` switch
 (e.g. `C:\Python33\python.exe -m vod_metadata`):

```
C:\Videos>C:\Python33\python.exe -m vod_metadata
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
 (`instance.D_ams`, `instance.D_app`, `instance.D_content`).
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

Maybe you suspect that your metadata is describing the wrong file?

```python
>>> vod_package.D_app["preview"]["Content_CheckSum"]
'05b441362eccbde82a98fabcafe071c1',
>>> vod_package.D_app["preview"]["Content_FileSize"]
'65116808'
```

You can update it to describe the correct one:

```python
>>> vod_package.check_files()
>>> vod_package.D_app["preview"]["Content_CheckSum"]
'2680090e51970e67b412af35201b9053'
>>> vod_package.D_app["preview"]["Content_FileSize"]
'44704888'
```

Have and XML file for an asset you need to delete?
```python
>>> vod_package.make_delete()
>>> vod_package.D_ams["package"]["Verb"]
'DELETE'
```

Save your edited file like so:

```python
>>> s = vod_package.write_xml()
>>> with open("rewritten.xml", 'wb') as outfile:
...     outfile.write(s)
```

## Library reference
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
* `self.has_preview` - `True` if there is a preview element, `False` otherwise.
* `self.has_poster` - `True` if there is a poster element, `False` otherwise.
* `self.is_update` - `True` if the AMS data for the package indicates that the
 `Version_Major` is something other than `1`, `False` otherwise.
* `self.is_delete` - `True` if the AMS data for the package has
 `"Verb" = "DELETE"`, `False` otherwise.

The `VodPackage` class exposes these methods:
* `VodPackage.write_xml(self, rewrite=False)` - Creates a new XML file that
 reflects any edits you've made to the metadata. Returns a `bytes` object that
 can be written to a file.
  * If `rewrite` is `False` then the content files specified by the `Content`
 tags won't be checked for existence or consistency with the supplied metadata.
  * If `rewrite` is True then the content files will be checked with
 `VodPackage.check_files()`.
* `VodPackage.check_files(self)` - Calls MediaInfo and sets the following
 attributes (if applicable) for each of the asset elements: `Content_FileSize`,
 `Content_CheckSum`, `Run_Time`, `Display_Run_Time`, `Codec`, `Audio_Type`,
 `Resolution`, `Frame Rate`, and `Bit_Rate`.
* `VodPackage.remove_preview(self)` - deletes the preview element from the asset
 package, if there is one to delete.
* `VodPackage.remove_poster(self)` - deletes the poster element from the asset
 package, if there is one to delete.
* `VodPackage.make_update(self)` - increments all the `Version_Major` values and
 marks the package as a metadata update.
* `VodPackage.make_delete(self)` - sets the `Verb` value to `DELETE` amd marks
 the package as a metadata update.
* `VodPackage.list_files(self)` - returns a tuple with the PID/PAID pairs for
 the package asset; title asset; and asset elements, as well as the content
 files for the asset elements. I might remove this method in the future.

## Contact the author
I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail [Bo Bayles](bbayles+github@gmail.com) with questions and feature suggestions.
