# **tess-locator**

**Where is my favorite star or galaxy in NASA's TESS Full Frame Image data set?**

`tess-locator` is a user-friendly package which combines the tess-point and tess-cloud packages to enable the positions of astronomical objects in the TESS data set to be queried in a fast and friendly way.

## Example use

Converting celestial coordinates to TESS pixel coordinates:

```python
>>> from tess_locator import locate
>>> locate("Alpha Cen")
List of 3 coordinates
↳[TessCoord(sector=11, camera=2, ccd=2, column=1699.1, row=1860.3, time=None)
  TessCoord(sector=12, camera=2, ccd=1, column=359.9, row=1838.7, time=None)
  TessCoord(sector=38, camera=2, ccd=2, column=941.1, row=1953.7, time=None)]
```

Obtaining pixel coordinates for a specific time:

```python
>>> locate("Alpha Cen", time="2019-04-28")
List of 1 coordinates
↳[TessCoord(sector=11, camera=2, ccd=2, column=1699.1, row=1860.3, time=2019-04-28 00:00:00)]
```


Obtaining pixel coordinates for a specific celestial coordinate:

```python
>>> from astropy.coordinates import SkyCoord
>>> crd = SkyCoord(ra=60, dec=70, unit='deg')
>>> locate(crd)
List of 4 coordinates
↳[TessCoord(sector=19, camera=2, ccd=2, column=355.3, row=1045.9, time=None)
    TessCoord(sector=25, camera=4, ccd=4, column=1107.0, row=285.9, time=None)
    TessCoord(sector=26, camera=4, ccd=3, column=317.7, row=395.9, time=None)
    TessCoord(sector=52, camera=4, ccd=4, column=603.5, row=240.2, time=None)]
```

You can access the properties of `TessCoord` objects using standard list and attribute syntax:


```python
>>> crdlist = locate("Alpha Cen")
>>> crdlist[0].sector, crdlist[0].camera, crdlist[0].ccd
(11, 2, 2)
>>> crdlist[0].column, crdlist[0].row
(1699.0540739785683, 1860.2510951146114)
```

When you have obtained a `TessCoord` object, you can use it to obtain a list of the TESS Full Frame Images (FFIs) which covered the position.
The objects returned are provided by the `tess-cloud <https://github.com/SSDataLab/tess-cloud>`_ package.

```python
>>> crdlist[0].list_images()
List of 1248 images
↳[TessImage("tess2019113062933-s0011-2-2-0143-s_ffic.fits")
    TessImage("tess2019113065933-s0011-2-2-0143-s_ffic.fits")
    TessImage("tess2019113072933-s0011-2-2-0143-s_ffic.fits")
    TessImage("tess2019113075933-s0011-2-2-0143-s_ffic.fits")
    ...
    TessImage("tess2019140065932-s0011-2-2-0143-s_ffic.fits")
    TessImage("tess2019140072932-s0011-2-2-0143-s_ffic.fits")
    TessImage("tess2019140075932-s0011-2-2-0143-s_ffic.fits")
    TessImage("tess2019140082932-s0011-2-2-0143-s_ffic.fits")]
```