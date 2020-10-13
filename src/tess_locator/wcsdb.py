"""Implements a database holding World Coordinate System (WCS) data for TESS.

The functions in this module serve to populate and query a simple single-file
data base which holds WCS data for TESS Full Frame Images across all sectors.

WCS DB contains the following columns:
sector, camera, ccd, begin, end, wcs 
"""
import itertools
from functools import lru_cache
from pathlib import Path
import warnings

from typing import Union

from astropy.wcs import WCS
from astropy.time import Time

import numpy as np
import pandas as pd
from pandas import DataFrame

from . import imagelist, log, SECTORS, DATADIR

# Where do we store all the WCS data?
WCS_DB: Path = DATADIR / Path("tess-wcs-all-sectors.parquet")


def populate_wcs_db():
    """Write WCS data of all sectors to a Parquet file.

    This function is slow (few minutes) because it will download the header
    of a reference FFI for each sector/camera/ccd combination.
    """
    log.info(f"Writing {WCS_DB}")
    summary = []
    for sector, camera, ccd in itertools.product(range(1, SECTORS+1), [1, 2, 3, 4], [1, 2, 3, 4]):
        images = imagelist.list_images(sector=sector, camera=camera, ccd=ccd)
        wcs = images[len(images) // 2].download_wcs().to_header_string(relax=True)
        data = {'sector': sector,
                'camera': camera,
                'ccd': ccd,
                'begin': images[0].begin,
                'end': images[-1].end,
                'wcs': wcs
                }
        summary.append(data) 
    df = pd.DataFrame(summary)
    df.to_parquet(WCS_DB)


@lru_cache
def load_wcs_db() -> DataFrame:
    """Reads the DataFrame that contains all WCS data."""
    log.info(f"Reading {WCS_DB}")
    return pd.read_parquet(WCS_DB)


@lru_cache(maxsize=4096)
def get_wcs(sector: int, camera: int, ccd: int) -> WCS:
    """Returns a WCS object for a specific FFI ccd."""
    df = load_wcs_db()
    wcsstr = df.query(f"sector == {sector} & camera == {camera} & ccd == {ccd}").iloc[0].wcs
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="'datfix' made the change 'Set DATE-REF to '1858-11-17' from MJD-REF'.")
        wcs = WCS(wcsstr)
    return wcs


@lru_cache
def time_to_sector(time: Union[str, Time]) -> int:
    """Returns the sector number for a given timestamp."""
    if isinstance(time, str):
        time = Time(time)

    db = load_wcs_db()
    begin = Time(np.array(db.begin, dtype=str), format='iso')
    end = Time(np.array(db.end, dtype=str), format='iso')
    mask = (time >= begin) & (time <= end)
    if mask.sum() > 0:
        return db[mask].iloc[0].sector
    return None
