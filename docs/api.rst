.. api:

API reference
=============

Notes and assumptions
---------------------

This library makes some assumptions about VOD metadata that you might
need to keep in mind:

*   Asset packages must have one ``movie`` asset element.
*   Asset packages *may* have zero or one ``preview``, ``poster``, or
    ``box cover`` asset elements.
*   Asset packages may not have any other types of asset element (even though
    the spec allows for custom ones).
*   Metadata updates may not alter the asset elements in the package (i.e. the
    ``preview``, ``poster``, or ``box cover`` asset elements cannot be
    removed).

VodPackage class
----------------

The ``VodPackage`` class is defined in the ``vod_metadata.VodPackage``
sub-module. Import it with:

.. code-block:: python

    from vod_metadata import VodPackage

Parse an existing metadata file by instantiating a VodPackage class:

.. code-block:: python

    vod_package = VodPackage(path_to_xml)

VodPackage attributes
---------------------

``VodPackage.__init__(self, xml_path)`` parses the file given by the
``xml_path`` argument. These attributes are exposed:

* ``instance.xml_path`` - the path to the XML file.
*   ``instance.tree`` - the XML tree as parsed by etree.
*   ``instance.D_ams`` - A dictionary of dictionaries to hold the "AMS"
    attributes. These identify the asset package, title asset, and asset elements.
    See the CableLabs specification for more information. The sub-dictionaries
    include:

    *   ``instance.D_ams["package"]``, ``instance.D_ams["title"]``, and ``instance.D_ams["movie"]``. These are required.
    *    ``instance.D_ams["preview"]`` and ``instance.D_ams["poster"]``. These are optional.

*   ``instance.D_app`` - A dictionary of dictionaries to hold the "App_Data"
    attributes. These describe the assets identified by the AMS sections. As with the AMS
    data, these sub-dictionaries are included:

    * ``instance.D_app["package"]``, ``instance.D_app["title"]``, and ``instance.D_app["movie"]``. These are required.
    * ``instance.D_app["preview"]``, ``instance.D_app["poster"]``, ``instance.D_app["box cover"]``. These are optional.

*   ``instance.has_preview`` - ``True`` if there is a preview element, ``False`` otherwise.
*   ``instance.has_poster`` - ``True`` if there is a poster element, ``False`` otherwise.
*   ``instance.has_box_cover`` - ``True`` if there is a box cover element, ``False`` otherwise.
*   ``instance.is_update`` - ``True`` if the AMS data for the package indicates that the ``Version_Major`` is something other than ``1``, ``False`` otherwise.
*   ``instance.is_delete`` - ``True`` if the AMS data for the package has ``"Verb" = "DELETE"``, ``False`` otherwise.

VodPackage methods
------------------

The ``VodPackage`` class exposes these methods:

*   ``VodPackage.write_xml(rewrite=False)`` - Creates a new XML file that
    reflects any edits you've made to the metadata. Returns a ``bytes`` object that
    can be written to a file.

    *   If ``rewrite`` is ``False`` then the content files specified by the
        ``Content`` tags won't be checked for existence or consistency with the
        supplied metadata.
    *   If ``rewrite`` is True then the content files will be checked with
        ``VodPackage.check_files()``.

*   ``VodPackage.overwrite_xml(rewrite=False)`` - Calls ``VodPackage.write_xml``,
    optionally with ``rewrite``. Saves the result over the original XML file.
*   ``VodPackage.check_files()`` - Calls MediaInfo and sets the following
    attributes (if applicable) for each of the asset elements: ``Content_FileSize``,
    ``Content_CheckSum``, ``Run_Time``, ``Display_Run_Time``, ``Codec``, ``Audio_Type``,
    ``Resolution``, ``Frame Rate``, and ``Bit_Rate``.
*   ``VodPackage.remove_preview()`` - deletes the preview element from the asset package, if there is one to delete.
*   ``VodPackage.remove_poster()`` - deletes the poster element from the asset package, if there is one to delete.
*   ``VodPackage.remove_box_cover()`` - deletes the box cover element from the asset package, if there is one to delete.
*   ``VodPackage.make_update()`` - increments all the ``Version_Major`` values and
     marks the package as a metadata update. Content tags will not be written when
     using ``instance.write_xml()``. See the note above about the assumptions the
     library makes about updates for previously-delivered packages!
*   ``VodPackage.make_delete()`` - sets the ``Verb`` value to ``DELETE`` amd marks
    the package as a metadata update.


Exceptions
----------

The ``vod_metadata`` module exposes these exceptions:

*   ``MissingElement`` - raised if you try to write an asset package without a ``movie``
    element, if you use MediaInfo to scan an element that is missing, or if you
    try to remove an element that is not present.
*   ``InvalidMpeg`` - raised if you scan a video file and MediaInfo returns something
    not recognized as valid by the spec. See section 5.3.1 of MD-SP-VOD-CONTENT1.1 .
*   ``MediaInfoError`` - raised if you scan a video or picture file and MediaInfo
    doesn't return all the necessary information.
*   ``ConfigurationError`` - raised if the values specified in the configuration
    file, ``vod_config.ini`` are not valid.
