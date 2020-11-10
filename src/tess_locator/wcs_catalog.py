"""Implements a database holding World Coordinate System (WCS) data for TESS.

The functions in this module serve to populate and query a simple single-file
data base which holds WCS data for TESS Full Frame Images across all sectors.

The WCS catalog is a DataFrame composed of six columns:
sector, camera, ccd, begin, end, wcs. 
"""
import itertools
import warnings
from functools import lru_cache
from pathlib import Path
from typing import Union

import pandas as pd
from astropy.time import Time
from astropy.wcs import WCS
from pandas import DataFrame
from tqdm import tqdm

from . import DATADIR, SECTORS, imagelist, log


def _wcs_catalog_path(sector: int) -> Path:
    """Returns the filename of the WCS catalog of a given sector."""
    return DATADIR / Path(f"tess-s{sector:04d}-wcs-catalog.parquet")


def update_wcs_catalog(sector: int):
    """Write WCS data of a sector to a Parquet file.

    This function is slow (few minutes) because it will download the header
    of a reference FFI for each camera/ccd combination.
    """
    summary = []
    iterator = itertools.product([1, 2, 3, 4], [1, 2, 3, 4])
    for camera, ccd in tqdm(
        iterator, desc=f"Downloading sector {sector} headers", total=16
    ):
        images = imagelist.list_images(sector=sector, camera=camera, ccd=ccd)
        wcs = images[len(images) // 2].download_wcs().to_header_string(relax=True)
        data = {
            "sector": sector,
            "camera": camera,
            "ccd": ccd,
            "begin": images[0].begin,
            "end": images[-1].end,
            "wcs": wcs,
        }
        summary.append(data)
    df = pd.DataFrame(summary)
    path = _wcs_catalog_path(sector)
    log.info(f"Started writing {path}")
    df.to_parquet(path)
    log.info(f"Finished writing {path}")


@lru_cache()
def load_wcs_catalog(sector: int = None) -> DataFrame:
    """Reads the DataFrame that contains all WCS data."""
    if sector is None:
        sector = range(1, SECTORS + 1)
    else:
        sector = [sector]

    df = pd.concat([load_one_wcs_catalog(s) for s in sector])
    return df


def load_one_wcs_catalog(sector: int) -> DataFrame:
    path = _wcs_catalog_path(sector)
    log.info(f"Reading {path}")
    return pd.read_parquet(path)


@lru_cache(maxsize=4096)
def get_wcs(sector: int, camera: int, ccd: int) -> WCS:
    """Returns a WCS object for a specific FFI ccd."""
    df = load_wcs_catalog()
    wcsstr = (
        df.query(f"sector == {sector} & camera == {camera} & ccd == {ccd}").iloc[0].wcs
    )
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="'datfix' made the change 'Set DATE-REF to '1858-11-17' from MJD-REF'.",
        )
        wcs = WCS(wcsstr)
    return wcs


@lru_cache()
def get_sector_dates() -> DataFrame:
    """Returns a DataFrame with sector, begin, end."""
    db = load_wcs_catalog()
    begin = db.groupby("sector")["begin"].min()
    end = db.groupby("sector")["end"].max()
    return begin.to_frame().join(end)


@lru_cache()
def time_to_sector(time: Union[str, Time]) -> int:
    """Returns the sector number for a given timestamp."""
    if isinstance(time, Time):
        time = time.iso

    dates = get_sector_dates()
    for row in dates.itertuples():
        if (time >= row.begin) & (time <= row.end):
            return row.Index

    return None
