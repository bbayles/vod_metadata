.. generator:

Automatic metadata generator
============================

You can use the metadata generator to create XML metadata for video files.

Basic usage
-----------

Start by switching to a directory with some video files (e.g. ``cd C:\videos``):

.. code-block:: doscon

    C:\Videos>dir /b
    11 Pink.mpg
    12 Banker.mpg
    13 Game.mpg

Execute the script with the Python interpreter, using the ``-m`` switch:

.. code-block:: doscon

    C:\Videos> python -m vod_metadata

After it runs (it can take a bit for the checksums to be calculated) you should
have minimal valid metadata files for the videos in the directory:

.. code-block:: doscon

    C:\Videos>dir /b
    11 Pink.mpg
    11 Pink_1442.xml
    12 Banker.mpg
    12 Banker_2743.xml
    13 Game.mpg
    13 Game_5056.xml

Including previews and posters
------------------------------

To incorporate a preview and/or poster element for the file ``something.mpg``:

*   Put a ``something_preview.mpg`` file in the same directory
*   Put a ``something_poster.bmp`` file in the same directory.
*   Put a ``something_box_cover.bmp`` file in the same directory.

The preview file must have the same extension as the movie file,
and the poster / box cover can have either a .bmp or .jpg extension.

Command line options
--------------------

Process videos in a particular directory with the ``--video-dir`` argument.

.. code-block:: doscon

    C:\Videos>python -m vod_metadata  --video-dir "C:\Somewhere\Videos"

Specify a different metadata template (useful for adding custom values) with
the ``--template-path`` argument.

.. code-block:: doscon

    C:\Videos>python -m vod_metadata  --template-path "C:\Somewhere\template.xml"

Change what values are used when generating metadata files by specifying the
path to a config file (`example <https://github.com/bbayles/vod_metadata/blob/master/vod_metadata/vod_config.ini>`_):

.. code-block:: doscon

    C:\Videos>python -m vod_metadata  --config-path "C:\Somewhere\config.ini"

Troubleshooting
----------------

If you find that you get a ``RuntimeError: MediaInfo not found.`` error
message, you can specify the path to MediaInfo on the command line:

.. code-block:: doscon

    C:\Videos>python -m vod_metadata  --mediainfo-path "C:\Somewhere\MediaInfo.exe"

Be sure that you've got the command line (CLI) version of MediaInfo and not the
GUI version.
