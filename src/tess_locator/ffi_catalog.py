"""Implements a minimalist database of TESS FFI images.

The database is stored in Parquet files ("data/tess-sxxxx-ffi-catalog.parquet").
"""
# TEST IDEAS
# * add test to check that number of FFIs matches those in the bulk download script
# * number of FFI images should always be a multiple of four

import logging
from functools import lru_cache
from pathlib import Path

import pandas as pd
from astropy.table import Table
from astropy.time import Time
from pandas import DataFrame

from . import DATADIR, SECTORS

log = logging.getLogger(__name__)


@lru_cache()
def _mast_ffi_query(sector: int) -> Table:
    """Returns a list of all TESS FFIs for a given Sector."""
    # Local import of astroquery because it is an optional dependency
    from astroquery.utils.tap.core import TapPlus

    mast_tap = TapPlus(url="https://vao.stsci.edu/caomtap/tapservice.aspx")
    adql = f"""SELECT access_url, t_min, t_max FROM obscore
               WHERE obs_collection='TESS' AND dataproduct_type = "image"
               AND obs_id LIKE 'tess%-s{sector:04d}-%'"""
    log.info(f"Sending TAP query to MAST for sector {sector}.")
    log.debug(adql)
    job = mast_tap.launch_job_async(adql)
    return job.get_results()


def _query_ffi_catalog(sector: int) -> DataFrame:
    """Returns a DataFrame listing the FFI images for a given sector."""
    tbl = _mast_ffi_query(sector=sector)
    log.info(f"Found {len(tbl)} FFIs for sector {sector}.")
    df = tbl.to_pandas()
    df["filename"] = df["access_url"].str.split("/").str[-1]
    # Extract sector, camera, and ccd from the filename encoding
    df["sector"] = df["filename"].str.extract(r".*-s(\d+)-.*").astype(int)
    df["camera"] = df["filename"].str.extract(r".*-s\d+-(\d)-.*").astype(int)
    df["ccd"] = df["filename"].str.extract(r".*-s\d+-\d-(\d)-.*").astype(int)
    # Convert begin and end time from MJD to an ISO timestamp
    df["start"] = pd.Series(Time(df["t_min"], format="mjd").iso).str.slice(stop=19)
    df["stop"] = pd.Series(Time(df["t_max"], format="mjd").iso).str.slice(stop=19)
    df = df.sort_values("filename")
    return df[["filename", "sector", "camera", "ccd", "start", "stop"]]


def _ffi_catalog_path(sector: int) -> Path:
    """Returns the filename of the FFI catalog of a given sector."""
    return DATADIR / Path(f"tess-s{sector:04d}-ffi-catalog.parquet")


def update_ffi_catalog(sector, path=None, overwrite=False) -> DataFrame:
    if path is None:
        path = _ffi_catalog_path(sector=sector)
    if not overwrite and Path(path).exists():
        log.info(
            f"Skipping sector {sector}: file already exists ({path}).  Use `overwrite=True` to force-update."
        )
        return None
    df = _query_ffi_catalog(sector=sector)
    log.info(f"Started writing {path}")
    df.to_parquet(path, compression="gzip")
    log.info(f"Finished writing {path}")
    return df


def update_all_catalogs():
    for sector in range(1, SECTORS + 1):
        log.info(f"Fetching sector {sector}/{SECTORS}")
        update_ffi_catalog(sector=sector)


@lru_cache()
def load_ffi_catalog(sector: int) -> DataFrame:
    path = _ffi_catalog_path(sector=sector)
    log.info(f"Reading {path}")
    return pd.read_parquet(path)
