"""Script to update the FFI database that powers `tess-locator`.

Usage
=====
$ python -m tess_locator.update
"""
from .healpix import write_healpix_lookup_table


def update():
    write_healpix_lookup_table()


if __name__ == "__main__":
    update()
