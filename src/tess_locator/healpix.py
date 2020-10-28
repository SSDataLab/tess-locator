"""Implements a faster version of `locate()` using Healpix indexing."""
import json
import itertools
from collections import defaultdict
from typing import Union
import warnings

import numpy as np

from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord, ICRS
from astropy.time import Time
from astropy.wcs import NoConvergence

from tess_locator.wcsdb import get_wcs, time_to_sector
from tess_locator import TessCoord, TessCoordList
from tess_locator import SECTORS


HEALPIX_NSIDE = 128
HEALPIX_DB_FILENAME = 'healpix-index.json'


class HealpixLocator():
    
    def __init__(self, dbfile=HEALPIX_DB_FILENAME):
        with open(HEALPIX_DB_FILENAME) as fp:
            self.db = json.load(fp, object_hook=lambda d: {int(k): v for k, v in d.items()})
        self.hp = HEALPix(nside=HEALPIX_NSIDE, frame=ICRS())
    
    def skycoord_to_ccdlist(self, crd):
        #idx = hl.hp.skycoord_to_healpix(crd)
        # `lonlat_` seems a factor 2x faster than `skycoord_to_healpix`
        idx = hl.hp.lonlat_to_healpix(crd.ra, crd.dec)
        return self.db.get(idx, [])
    
    def locate(self, target: Union[str, SkyCoord], time: Union[str, Time] = None, sector: int = None) -> TessCoordList:
        if isinstance(target, SkyCoord):
            crd = target
        else:
            crd = SkyCoord.from_name(target)

        if crd.shape != ():
            raise ValueError("Only single-valued SkyCoord objects are supported.")
            
        sector_time = None
        if time:
            sector_time = [time_to_sector(time)]
            if sector_time is None:
                return TessCoordList([])

        if sector is not None:
            sector_time = np.atleast_1d(sector)
            
        ccdlist = self.skycoord_to_ccdlist(target)
        result = []
        for sctr, camera, ccd in ccdlist:
            if sector_time and sctr not in sector_time:
                continue
            wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message="All-NaN slice encountered")
                    # Using `wcs_` instead of `all_world2pix` would be faster but introduce errors >20px
                    pixel = wcs.all_world2pix(crd.ra, crd.dec, 1, tolerance=0.1)
                    tesscrd = TessCoord(sctr, camera, ccd, column=pixel[0], row=pixel[1])
                    result.append(tesscrd)
            except (NoConvergence, ValueError):
                pass
        return TessCoordList(result)


def healpix_lookup_generator():
    hp = HEALPix(nside=HEALPIX_NSIDE, frame=ICRS())
    healpix_index = defaultdict(list)

    sector = range(1, SECTORS+1)
    for sctr, camera, ccd in itertools.product(sector, [1, 2, 3, 4], [1, 2, 3, 4]):
        wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
        center_crd = wcs.pixel_to_world(1024, 1024)
        # Center-to-corner distance of a TESS CCD is approx ~8.1 degrees,
        # so we request the HealPix values across a cone centered on the
        # center of the CCD with a radius of 8.5 degrees.
        result = hp.cone_search_skycoord(center_crd, radius=8.5*u.deg)
        for idx in result:
            healpix_index[int(idx)].append((sctr, camera, ccd))

    with open(HEALPIX_DB_FILENAME, 'w') as fp:
        json.dump(healpix_index, fp)
