"""Script to update the FFI database that powers `tess-locator`.

Usage
=====
$ python -m tess_locator.update
"""
from .ffi_catalog import update_ffi_catalog
from .wcs_catalog import update_wcs_catalog
from .healpix import update_healpix_lookup_table


def update(sector: int):
    update_ffi_catalog(sector=sector)
    update_wcs_catalog(sectors=sector)
    update_healpix_lookup_table()


if __name__ == "__main__":
    update(28)
