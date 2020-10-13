tess-locator
============

**Fast offline queries of TESS FFI positions and filenames.**

`tess-locator` is a user-friendly package which provides fast offline access to an embedded database of TESS meta data.
It allows TESS pixel coordinates and FFI filenames to be queried in a fast way without requiring internet access.

Example use
-----------

Converting celestial to pixel coordinates:

.. code-block:: python

    >>> from tess_locator import locate
    >>> locate("Alpha Cen")
    List of 2 coordinates
    ↳[TessCoord(sector=11, camera=2, ccd=2, column=1700.2, row=1860.3)
      TessCoord(sector=12, camera=2, ccd=1, column=360.7, row=1838.8)]


Obtaining pixel coordinates for a specific time:

.. code-block:: python

    >>> locate("Alpha Cen", time="2019-04-28 00:00:00")
    List of 1 coordinates
    ↳[TessCoord(sector=11, camera=2, ccd=2, column=1700.2, row=1860.3)]


Obtaining FFI image meta data:

.. code-block:: python

    >>> locate("Alpha Cen")[0].get_images()
    List of 1248 images
    ↳[TessImage(filename='tess2019113062933-s0011-2-2-0143-s_ffic.fits', begin='2019-04-23 06:34:41', end='2019-04-23 07:04:41')
      TessImage(filename='tess2019113065933-s0011-2-2-0143-s_ffic.fits', begin='2019-04-23 07:04:41', end='2019-04-23 07:34:41')
      TessImage(filename='tess2019113072933-s0011-2-2-0143-s_ffic.fits', begin='2019-04-23 07:34:41', end='2019-04-23 08:04:41')
      TessImage(filename='tess2019113075933-s0011-2-2-0143-s_ffic.fits', begin='2019-04-23 08:04:41', end='2019-04-23 08:34:41')
      ...
      TessImage(filename='tess2019140065932-s0011-2-2-0143-s_ffic.fits', begin='2019-05-20 07:05:08', end='2019-05-20 07:35:08')
      TessImage(filename='tess2019140072932-s0011-2-2-0143-s_ffic.fits', begin='2019-05-20 07:35:08', end='2019-05-20 08:05:08')
      TessImage(filename='tess2019140075932-s0011-2-2-0143-s_ffic.fits', begin='2019-05-20 08:05:08', end='2019-05-20 08:35:08')
      TessImage(filename='tess2019140082932-s0011-2-2-0143-s_ffic.fits', begin='2019-05-20 08:35:08', end='2019-05-20 09:05:08')]


Documentation
-------------

Please visit the `tutorial <https://github.com/SSDataLab/tess-locator/blob/master/docs/tutorial.ipynb>`_.


Similar packages
----------------

* `tess-point <https://github.com/christopherburke/tess-point>`_ uses a theoretical pointing model rather than the WCS data. It should agree with the WCS results to within 1-2 pixels. Compared to `tess-point`, we add a user-friendly API and the ability to specify the time, which is important for moving objects.
* `astroquery.mast <https://astroquery.readthedocs.io/en/latest/mast/mast.html>`_ includes the excellent ``TesscutClass.get_sectors()`` method which queries a web API. This package provides an offline version of that service, and adds the ability to query by time.
* `tess-waldo <https://github.com/SimonJMurphy/tess-waldo>`_ lets you visualize how a target moves over the detector across sectors. It queries the ``TessCut`` service to obtain this information. This package adds the ability to create such plots offline.
