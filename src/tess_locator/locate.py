import itertools
import warnings
from typing import Union

import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.wcs import NoConvergence

from . import SECTORS, TessCoord, TessCoordList
from .healpix import HealpixLocator
from .wcs_catalog import get_wcs, time_to_sector


def locate(
    target: Union[str, SkyCoord], time: Union[str, Time] = None, sector: int = None
) -> TessCoordList:
    hloc = HealpixLocator()
    return hloc.locate(target=target, time=time, sector=sector)


def _locate_slow(
    target: Union[str, SkyCoord], time: Union[str, Time] = None, sector: int = None
) -> TessCoordList:
    """Returns a `TessCoordList.

    `target` only accepts a single-valued SkyCoord to avoid ambiguity between
    multiple targets vs multiple sector observations of one target.
    """
    if isinstance(target, SkyCoord):
        crd = target
    else:
        crd = SkyCoord.from_name(target)

    if crd.shape != ():
        raise ValueError("Only single-valued SkyCoord objects are supported.")

    if time:
        sector = time_to_sector(time)
        if sector is None:
            return TessCoordList([])

    if sector is None:
        sector = range(1, SECTORS + 1)
    else:
        sector = np.atleast_1d(sector)

    result = []
    for sctr, camera, ccd in itertools.product(sector, [1, 2, 3, 4], [1, 2, 3, 4]):
        wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="All-NaN slice encountered")
                pixel = wcs.all_world2pix(crd.ra, crd.dec, 1)
                tesscrd = TessCoord(sctr, camera, ccd, column=pixel[0], row=pixel[1])
                result.append(tesscrd)
        except (NoConvergence, ValueError):
            pass
    return TessCoordList(result)
