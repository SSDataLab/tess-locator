"""Implements a faster version of `locate()` using Healpix indexing."""
import gzip
import itertools
import json
import warnings
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Union

import numpy as np
from astropy import units as u
from astropy.coordinates import ICRS, SkyCoord
from astropy.time import Time
from astropy.wcs import NoConvergence
from astropy_healpix import HEALPix
from tqdm import tqdm

from . import DATADIR, SECTORS, TessCoord, TessCoordList, log
from .tesscoord import COLUMN_RANGE, ROW_RANGE
from .wcs_catalog import get_wcs, time_to_sector

HEALPIX_NSIDE = 64
HEALPIX_DB_FILENAME = DATADIR / Path("healpix-index.json.gz")


class HealpixLocator:
    """Maps HealPix to (sector, camera, ccd) using a pre-computed lookup table."""

    def __init__(self, dbfile=HEALPIX_DB_FILENAME):
        self.db = load_healpix_table(dbfile)
        self.hp = HEALPix(nside=HEALPIX_NSIDE, frame=ICRS())

    def _skycoord_to_ccdlist(self, crd):
        """Returns a list of (sector, camera, ccd) tuples which likely observed
        the given coordinate `crd`.

        Note: the list returned is a super-set of the true list of observations,
        because it is approximated using healpix indexing.
        """
        # Note: `lonlat_to_healpix` seems a factor 2x faster than
        # `skycoord_to_healpix`, which is why we use it here.
        idx = self.hp.lonlat_to_healpix(crd.ra, crd.dec)
        return self.db.get(idx, [])

    def locate(
        self,
        target: Union[str, SkyCoord],
        time: Union[str, Time] = None,
        sector: int = None,
    ) -> TessCoordList:
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

        ccdlist = self._skycoord_to_ccdlist(crd)
        result = []
        for sctr, camera, ccd in ccdlist:
            if sector_time and sctr not in sector_time:
                continue
            wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings(
                        "ignore", message="All-NaN slice encountered"
                    )
                    # Using `wcs_` instead of `all_world2pix` would be faster but introduce errors >20px
                    pixel = wcs.all_world2pix(crd.ra, crd.dec, 1, tolerance=0.1)
                    tesscrd = TessCoord(
                        sctr, camera, ccd, column=pixel[0], row=pixel[1]
                    )
                    result.append(tesscrd)
            except (NoConvergence, ValueError):
                pass
        return TessCoordList(result)


@lru_cache()
def load_healpix_table(dbfile: str = HEALPIX_DB_FILENAME) -> dict:
    with gzip.open(HEALPIX_DB_FILENAME) as fp:
        return json.load(fp, object_hook=lambda d: {int(k): v for k, v in d.items()})


def create_healpix_table(nside: int = None) -> dict:
    """Returns a dictionary mapping healpix onto (sector, camera, ccd).

    Parameters
    ----------
    nside : int
        Healpix parameter.
    """
    if nside is None:
        nside = HEALPIX_NSIDE

    hp = HEALPix(nside=nside, frame=ICRS())
    healpix_lookup = defaultdict(list)

    sectors = range(1, SECTORS + 1)
    iterator = itertools.product(sectors, [1, 2, 3, 4], [1, 2, 3, 4])
    for sctr, camera, ccd in tqdm(iterator, total=len(sectors) * 4 * 4):
        wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
        center_crd = wcs.pixel_to_world(np.mean(COLUMN_RANGE), np.mean(ROW_RANGE))
        # Center-to-corner distance of a TESS CCD is approx ~8.5 degrees,
        # so we request the HealPix values across a cone centered on the
        # center of the CCD with a radius of 8.6 degrees.
        result = hp.cone_search_skycoord(center_crd, radius=8.6 * u.deg)
        for idx in result:
            healpix_lookup[int(idx)].append((sctr, camera, ccd))

    return healpix_lookup


def update_healpix_table(nside: int = None, output_fn: str = None) -> None:
    """Generates and stores the HEALPix lookup table."""
    if output_fn is None:
        output_fn = HEALPIX_DB_FILENAME
    healpix_lookup = create_healpix_table(nside=nside)
    log.info(f"Started writing {HEALPIX_DB_FILENAME}")
    with gzip.open(HEALPIX_DB_FILENAME, "wt") as fp:
        json.dump(healpix_lookup, fp)
    log.info(f"Finished writing {HEALPIX_DB_FILENAME}")
