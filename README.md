## Introduction
This project contains a library for manipulating and generating metadata files
that conform to the [CableLabs VOD Metada 1.1 specification](http://cablelabs.com/specification/cablelabs-video-on-demand-content-specification-version-1-1/).

## Quick start guide for the metadata generator
This project contains a script that will generate valid VOD metadata for all the
video files in a directory. This guide (written with Windows users who might
not be familiar with Python) shows how get that script up and running.

First, get the pre-requisites:
* Make sure you've got a recent version of [Python 3](http://python.org) installed. Versions 3.2 and up should work.
* Make sure you've got the [lxml](http://lxml.de) library installed. If you're on Windows you can use the installer from [Christoph Gohlke's Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)
* Download the [MediaInfo](http://mediaarea.net/en/MediaInfo) CLI archive and extract it somewhere (e.g. to `C:\Program Files\MediaInfo`).

Then, get the module ready:
* Download this module's [source archive from Github](http://github.com/bbayles/vod_metadata/zipball/master/). Then extract it to Python's `site-packages` directory (you should wind up with the files in e.g. `C:\Python33\lib\site-packages\vod_metadata`).
* Edit `template_values.ini` and set the path to the MediaInfo CLI executable and any custom parameters.

Finally, run the script:
* Open up a command prompt and switch to a directory with video files (e.g. `C:\videos`)
* Execute the script with the Python interpreter, using the `-m` switch (e.g. `C:\Python33\python.exe -m vod_metadata`)

After it runs (it can take a bit for the checksums to be calculated) you should have minimal valid metadata files for the videos in the directory.

**Before**:
```
C:\Users\Bo\Videos>dir /b
11 Pink.mpg
12 Banker.mpg
13 Game.mpg
```

**During**:
```
C:\Users\Bo\Videos>C:\Python33\python.exe -m vod_metadata
Processing 11 Pink.mpg...
Processing 12 Banker.mpg...
Processing 13 Game.mpg...
```

**After**:
```
C:\Users\Bo\Videos>dir /b
11 Pink.mpg
11 Pink_1442.xml
12 Banker.mpg
12 Banker_2743.xml
13 Game.mpg
13 Game_5056.xml
```

## Using the library
You can use the module to edit already-existing metadata files also.

First, import the module and switch to the directory where your video, metadata, and poster files are located:
```
>>> from vod_metadata import VodPackage
>>> import os
>>> os.chdir("C:/Users/Bo/Videos")
```

Next, read in an existing metadata file:
```
>>> vod_package = VodPackage("The Hounds of Baskerville.xml")
```

You can now read and edit the metadata through Python dictionaries (`VodPackage.D_ams`, `VodPackage.D_app`, `VodPackage.D_content`):
```
>>> vod_package.D_ams["title"]["Asset_ID"]
0: 'MSOT2014020814473655'
```

There are some convenience functions, such as `VodPackage.has_preview()` and `VodPackage.has_poster()`:
```
>>> vod_package.has_preview
1: True
>>> vod_package.has_poster
2: False
```

You can use `VodPackage.check_files()` to scan the files described by the metadata and update the metadata:
```
>>> vod_package.D_app["preview"]["Content_CheckSum"]
3: '05b441362eccbde82a98fabcafe071c1',
>>> vod_package.D_app["preview"]["Content_FileSize"]
4: '65116808'
>>> vod_package.check_files()
>>> vod_package.D_app["preview"]["Content_CheckSum"]
5: '2680090e51970e67b412af35201b9053'
>>> vod_package.D_app["preview"]["Content_FileSize"]
6: '44704888'
```

Write your edits with `VodPackage.write_xml()`. You can save the result to a new file:
```
>>> s = vod_package.write_xml()
>>> with open("rewritten.xml", 'wb') as outfile:
...     outfile.write(s)
```

## Contact the author
I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail [Bo Bayles](bbayles+github@gmail.com) with questions and feature suggestions.
