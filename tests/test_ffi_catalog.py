from tess_locator import SECTORS
from tess_locator.ffi_catalog import load_ffi_catalog


def test_ffi_catalog_contents():
    for sector in range(1, SECTORS + 1):
        # Is a catalog for each sector available?
        catalog = load_ffi_catalog(sector=sector)
        assert all(catalog.sector == sector)
        # Does each camera have the same number of rows?
        n_rows_camera1 = (catalog.camera == 1).sum()
        for camera in [2, 3, 4]:
            n_rows = (catalog.camera == camera).sum()
            assert n_rows == n_rows_camera1
