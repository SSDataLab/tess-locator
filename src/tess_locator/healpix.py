"""Implements a faster version of `locate()` using Healpix indexing."""
import json
import itertools
from collections import defaultdict
from typing import Union
import warnings
from functools import lru_cache
from pathlib import Path

from tqdm import tqdm
import numpy as np

from astropy_healpix import HEALPix
from astropy.coordinates import SkyCoord, ICRS
from astropy.time import Time
from astropy.wcs import NoConvergence
from astropy import units as u

from .wcsdb import get_wcs, time_to_sector
from .tesscoord import COLUMN_RANGE, ROW_RANGE
from . import TessCoord, TessCoordList
from . import SECTORS, DATADIR, log


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

        ccdlist = self._skycoord_to_ccdlist(target)
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


@lru_cache
def load_healpix_table(dbfile: str = HEALPIX_DB_FILENAME) -> dict:
    with open(HEALPIX_DB_FILENAME) as fp:
        return json.load(fp, object_hook=lambda d: {int(k): v for k, v in d.items()})


def create_healpix_lookup_table(nside: int = None) -> dict:
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

    sector = range(1, SECTORS + 1)
    combinations = itertools.product(sector, [1, 2, 3, 4], [1, 2, 3, 4])
    for sctr, camera, ccd in tqdm(combinations, total=len(sector) * 4 * 4):
        wcs = get_wcs(sector=sctr, camera=camera, ccd=ccd)
        center_crd = wcs.pixel_to_world(np.mean(COLUMN_RANGE), np.mean(ROW_RANGE))
        # Center-to-corner distance of a TESS CCD is approx ~8.5 degrees,
        # so we request the HealPix values across a cone centered on the
        # center of the CCD with a radius of 8.6 degrees.
        result = hp.cone_search_skycoord(center_crd, radius=8.6 * u.deg)
        for idx in result:
            healpix_lookup[int(idx)].append((sctr, camera, ccd))

    return healpix_lookup


def write_healpix_lookup_table(nside: int = None, output_fn: str = None) -> None:
    """Generates and stores the HEALPix lookup table."""
    if output_fn is None:
        output_fn = HEALPIX_DB_FILENAME
    log.info(f"Writing {HEALPIX_DB_FILENAME}")
    healpix_lookup = create_healpix_lookup_table(nside=nside)
    with open(HEALPIX_DB_FILENAME, "wt") as fp:
        json.dump(healpix_lookup, fp)
