tess-locator
============

**Where is my object in the TESS Full Frame Images?**

`tess-locator` is a fast and user-friendly package which uses the WCS headers of TESS Full Frame Images to determine the presence of an astronomical object in the Field of View of NASA's Transiting Exoplanet Survey Satellite (TESS).


Example use
-----------

.. code-block:: python

    >>> from tess_locator import locate
    >>> locate(skycoord, time="2020-10-01 14:02:43")
    TessCoord(sector=4, camera=2, ccd=2, col=514.2, row=126.7)


Similar packages
----------------

* `tess-point <https://github.com/christopherburke/tess-point>`_ uses a theoretical pointing model rather than the WCS data. It should agree with the WCS results to within 1-2 pixels. Compared to `tess-point`, we add a user-friendly API and the ability to specify the time, which is important for moving objects.
* `tess-waldo <https://github.com/SimonJMurphy/tess-waldo>`_ is a great package which lets you visualize how a target moves over the detector across sectors. It queries the TessCut service to obtain this information, which makes it a bit slower than this package.
* `astroquery.mast <https://astroquery.readthedocs.io/en/latest/mast/mast.html>`_ includes the excellent `TesscutClass.get_sectors()` method which uses a web API. In contrast, this package can be run without internet access.
