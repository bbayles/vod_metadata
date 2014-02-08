## Introduction
This project contains a library for manipulating and generating metadata files
that conform to the [CableLabs VOD Metada 1.1 specification](http://cablelabs.com/specification/cablelabs-video-on-demand-content-specification-version-1-1/).

Included is a tool designed to help import video files into a VOD back office by
generating valid metadata files. When you run the tool from a directory
containing video files it will generate an XML metadata file for each video file
in the directory.

## Requirements and installation:
* Download and install [Python](http://python.org/download/). This project was developed for version 3.3.
* Download the [MediaInfo](http://mediaarea.net/en/MediaInfo) CLI archive and extract it to some folder. This project was developed for version 0.7.67 .
* Download and install [lxml](http://lxml.de). This project was developed for version 3.3.0. Windows users can find binaries at [Christoph Gohlke's Python Extension Packages page](http://www.lfd.uci.edu/~gohlke/pythonlibs/).
* Download the project source archive and extract it to some folder.
* Edit the `template_values.ini` file from the source to specify the path to the MediaInfo CLI and to set custom parameters.

The project is written with Windows users in mind, but other platforms will
probably work with a bit of modification.

## Contact the author
I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail [Bo Bayles](bbayles+github@gmail.com) with questions and feature suggestions.
