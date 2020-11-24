from tess_locator import SECTORS
from tess_locator.wcs_catalog import load_wcs_catalog


def test_wcs_catalog():
    catalog = load_wcs_catalog()
    for sector in range(1, SECTORS + 1):
        assert sector in catalog.sector.values
        sector_catalog = catalog[catalog.sector == sector]
        # Does each camera have the same number of rows?
        n_rows_camera1 = (sector_catalog.camera == 1).sum()
        for camera in [2, 3, 4]:
            n_rows = (sector_catalog.camera == camera).sum()
            assert n_rows == n_rows_camera1
