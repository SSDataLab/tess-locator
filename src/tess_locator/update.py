"""Script to update the FFI database that powers `tess-locator`.

Usage
=====
$ python -m tess_locator.update SECTOR
"""
import typer

from . import log
from .ffi_catalog import update_ffi_catalog
from .healpix import update_healpix_table
from .wcs_catalog import update_wcs_catalog


def main(sector: int, overwrite: bool = False):
    """Download the FFI filenames and WCS headers for a sector, and update
    the HealPix table to include them in the `locate` function."""
    log.setLevel("INFO")
    update_ffi_catalog(sector=sector, overwrite=overwrite)
    update_wcs_catalog(sector=sector)
    update_healpix_table()


def update_all(last_sector: int):
    """Download all FFI filenames and WCS headers.

    Warning: this will take a long time!
    """
    log.setLevel("INFO")
    for sector in range(1, last_sector + 1):
        update_ffi_catalog(sector=sector, overwrite=True)
        update_wcs_catalog(sector=sector)
    update_healpix_table()


if __name__ == "__main__":
    typer.run(main)
    # update_all()
