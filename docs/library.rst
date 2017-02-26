.. generator:

Python library examples
=======================

You can use the library to read and edit already-existing metadata files.

Reading a metadata file
-----------------------

First, start up the Python interpreter (``python`` on the command line)
and then import the module:

.. code-block:: python

    >>> from vod_metadata import VodPackage

Next, open an existing metadata file:

.. code-block:: python

    >>> vod_package = VodPackage("C:/Videos/The Hounds of Baskerville.xml")

Accessing metadata attributes
-----------------------------

Once you've opened a file, its attributes will are available from the
``vod_package`` instance.
It stores them in dictionaries that correspond to the structure of the metadata
file:

*   **AMS data**: ``vod_package.D_ams``
*   **Application data**: ``vod_package.D_app``
*   **Content data**: ``vod_package.D_content``

Each dictionary will have sub-dictionary for the available classes of assets.
For example, to access the ``Provider_ID`` and ``Asset_ID`` for the title
asset:

.. code-block:: python

    >>> vod_package.D_ams["title"]["Provider_ID"]
    'example.com'
    >>> vod_package.D_ams["title"]["Asset_ID"]
    'MSOT2014020814473655'

You may modify the attribute dictionaries with normal assignment:

.. code-block:: python

    >>> vod_package.D_app["movie"]["Content_FileSize"] = 251405
    >>> vod_package.D_app["movie"]["Content_FileSize"]
    251405

Automatic updates
-----------------

To check whether an asset package contains a poster, look at the ``has_poster``
attribute. To remove the poster, call the ``remove_poster`` method:

.. code-block:: python

    >>> vod_package.has_poster
    True
    >>> vod_package.remove_poster()
    >>> vod_package.has_poster
    False

To fix up file sizes and checksums, call the ``check_files`` method.
It will overwrite the existing values with new ones computed by MediaInfo.

.. code-block:: python

    >>> vod_package.D_app["preview"]["Content_CheckSum"]
    '05b441362eccbde82a98fabcafe071c1',
    >>> vod_package.check_files()
    >>> vod_package.D_app["preview"]["Content_CheckSum"]
    '2680090e51970e67b412af35201b9053'

If you have a package you need to delete from you system, call the
``make_delete`` method.

.. code-block:: python

    >>> vod_package.make_delete()
    >>> vod_package.D_ams["package"]["Verb"]
    'DELETE'

Editing files and saving changes
--------------------------------

If you've made any modifications, you can save a new XML file with the changes
like so:

.. code-block:: python

    # Save a new version
    >>> s = vod_package.write_xml()
    >>> with open("altered.xml", 'wb') as outfile:
    ...     outfile.write(s)
    # Overwrite the original file
    >>> vod_package.overwrite_xml()
