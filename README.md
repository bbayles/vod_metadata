## Introduction
This project contains a library for manipulating and generating metadata files
that conform to the [CableLabs VOD Metada 1.1 specification](http://cablelabs.com/specification/cablelabs-video-on-demand-content-specification-version-1-1/).

## Quick start
This project contains a script that will generate valid VOD metadata for all the
video files in a directory. This guide (written with Windows users who might
not be familiar with Python) shows how get that script up and running.

First, get the pre-requisites:
* Make sure you've got a recent version of [Python 3](http://python.org) installed. Versions 3.2 and up should work.
* Make sure you've got the [lxml](http://lxml.de) library installed. If you're on Windows you can use the installer from [Christoph Gohlke's Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)
* Download the [MediaInfo](http://mediaarea.net/en/MediaInfo) CLI archive and extract it somewhere (e.g. to `C:\Program Files\MediaInfo`).

Then, get the module ready:
* Download this module's [source archive from Github](http://github.com/bbayles/vod_metadata/zipball/master/). Then extract it to Python's `site-packages` directory (you should wind up with the files in e.g. `C:\Python33\lib\site-packages\vod_metadata-master`).
* Edit `template_Values.ini` and set the path to the MediaInfo CLI executable and any custom parameters.

Finally, run the script:
* Open up a command prompt and switch to a directory with video files (e.g. `C:\videos`)
* Execute the script with the Python interpreter, using the `-m` switch (e.g. `C:\Python33\python.exe -m vod_metadata-master`)

After it runs (it can take a bit for the checksums to be calculated) you should have minimal valid metadata files for the videos in the directory.

## Contact the author
I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail [Bo Bayles](bbayles+github@gmail.com) with questions and feature suggestions.
