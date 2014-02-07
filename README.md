This project contains a library for manipulating and generating metadata files
that conform to the CableLabs VOD Metada 1.1 specification.
(http://cablelabs.com/projects/metadata/specifications/specifications11.html)

Included is a tool designed to help import video files into a VOD back office by
generating valid metadata files. When you run the tool from a directory
containing video files it will generate an XML metadata file for each video file
 in the directory.

This project requires Python (tested with version 3.3.3) and
MediaInfo (tested with version 0.7.67). You will need to download the MediaInfo
CLI executable from (http://mediainfo.sourceforge.net) and edit
template_values.ini to specify the path.

As of 2014 the generated can files have all the "Required" attributes in the
CableLabs specification, but the ones added in 2009 are not included by default.

Edit the template_values.ini file to set custom parameters. The default
parameters will produce valid metadata, but make sure to check that your system
can use it before trying to import the results.

I wrote this tool to save myself time hand-editing VOD metadata files.
I've tested importing the generated metadata into SeaChange Axiom and Arris CMM
back office systems.

E-mail Bo Bayles (bbayles@gmail.com) with questions and feature suggestions.