import itertools
import warnings

from typing import Union

from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.wcs import NoConvergence
import numpy as np

from .wcsdb import get_wcs, time_to_sector
from . import TessCoord, TessCoordList, SECTORS


def locate(target: Union[str, SkyCoord], time: Union[str, Time] = None, sector: int = None) -> TessCoordList:
    """Returns a `TessCoordList."""
    if isinstance(target, SkyCoord):
        crd = target
    else:
        crd = SkyCoord.from_name(target)

    if crd.shape != ():
        raise ValueError("Only single-valued SkyCoord objects are supported.")

    if time:
        sector = time_to_sector(time)

    if sector is None:
        sector = range(1, SECTORS+1)
    else:
        sector = np.atleast_1d(sector)

    result = []
    for sctr, camera, ccd in itertools.product(sector, [1, 2, 3, 4], [1, 2, 3, 4]):
        wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="All-NaN slice encountered")
                pixel = wcs.all_world2pix(crd.ra, crd.dec, 1)
                #if not (np.isnan(pixel[0]) or np.isnan(pixel[1])):
                tesscrd = TessCoord(sctr, camera, ccd, column=pixel[0], row=pixel[1])
                result.append(tesscrd)
        except (NoConvergence, ValueError):
            pass
    return TessCoordList(result)
