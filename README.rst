tess-locator
============

**Where is my favorite star or galaxy in NASA's TESS Full Frame Image data set?**

|pypi| |pytest| |black| |flake8| |mypy|

.. |pypi| image:: https://img.shields.io/pypi/v/tess-locator
                :target: https://pypi.python.org/pypi/tess-locator
.. |pytest| image:: https://github.com/SSDataLab/tess-locator/workflows/pytest/badge.svg
.. |black| image:: https://github.com/SSDataLab/tess-locator/workflows/black/badge.svg
.. |flake8| image:: https://github.com/SSDataLab/tess-locator/workflows/flake8/badge.svg
.. |mypy| image:: https://github.com/SSDataLab/tess-locator/workflows/mypy/badge.svg


`tess-locator` is a user-friendly wrapper around the `tess-point <https://github.com/christopherburke/tess-point>`_
package which allows the positions of astronomical objects in the TESS data set
to be queried in a fast and friendly way.


Installation
------------

.. code-block:: bash

    python -m pip install tess-locator

Example use
-----------

Converting celestial to pixel coordinates:

.. code-block:: python

    >>> from tess_locator import locate
    >>> locate("Alpha Cen")
    List of 3 coordinates
    ↳[TessCoord(sector=11, camera=2, ccd=2, column=1699.1, row=1860.3, time=None)
      TessCoord(sector=12, camera=2, ccd=1, column=359.9, row=1838.7, time=None)
      TessCoord(sector=38, camera=2, ccd=2, column=941.1, row=1953.7, time=None)]


Obtaining pixel coordinates for a specific time:

.. code-block:: python

    >>> locate("Alpha Cen", time="2019-04-28")
    List of 1 coordinates
    ↳[TessCoord(sector=11, camera=2, ccd=2, column=1699.1, row=1860.3, time=2019-04-28 00:00:00)]


Documentation
-------------

Please visit the `tutorial <https://github.com/SSDataLab/tess-locator/blob/master/docs/tutorial.ipynb>`_.


Similar packages
----------------

* `tess-point <https://github.com/christopherburke/tess-point>`_ is the package being called behind the scenes. Compared to `tess-point`, we add a user-friendly API and the ability to specify the time, which is important for moving objects.
* `astroquery.mast <https://astroquery.readthedocs.io/en/latest/mast/mast.html>`_ includes the excellent ``TesscutClass.get_sectors()`` method which queries a web API. This package provides an offline version of that service, and adds the ability to query by time.
* `tess-waldo <https://github.com/SimonJMurphy/tess-waldo>`_ lets you visualize how a target moves over the detector across sectors. It queries the ``TessCut`` service to obtain this information. This package adds the ability to create such plots offline.
