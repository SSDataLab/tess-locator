from collections import UserList
from typing import Union

import attr
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time
from pandas import DataFrame

from . import list_images
from .imagelist import TessImageList
from .wcs_catalog import get_wcs

# The science area of the TESS CCDs are bounded by:
# lower left corner: (column, row) = (45, 1)
# upper right corner: (column, row) = (2092, 2048)
# By convention, the pixel coordinates refer to the centers of pixels,
# so the valid ranges are:
COLUMN_RANGE = [44.5, 2092.5]
ROW_RANGE = [0.5, 2048.5]


@attr.s(slots=True)
class TessCoord:
    sector: int = attr.ib()
    camera: int = attr.ib(validator=attr.validators.in_([1, 2, 3, 4]))
    ccd: int = attr.ib(validator=attr.validators.in_([1, 2, 3, 4]))
    column: float = attr.ib(
        converter=float, repr=lambda value: f"{value:.1f}", default=np.nan
    )
    row: float = attr.ib(
        converter=float, repr=lambda value: f"{value:.1f}", default=np.nan
    )

    @column.validator
    def _validate_column(self, attribute, value):
        # if np.isnan(value):
        #    raise ValueError(f"'column' cannot be NaN")
        if value < COLUMN_RANGE[0] or value > COLUMN_RANGE[1]:
            raise ValueError(
                f"'column' must be in the range [{COLUMN_RANGE[0]}, {COLUMN_RANGE[1]}] (got {value})"
            )

    @row.validator
    def _validate_row(self, attribute, value):
        # if np.isnan(value):
        #    raise ValueError(f"'row' cannot be NaN")
        if value < ROW_RANGE[0] or value > ROW_RANGE[1]:
            raise ValueError(
                f"'row' must be in the range [{ROW_RANGE[0]}, {ROW_RANGE[1]}] (got {value})"
            )

    def get_images(self, time: Union[str, Time] = None) -> TessImageList:
        return list_images(
            sector=self.sector, camera=self.camera, ccd=self.ccd, time=time
        )

    def to_skycoord(self) -> SkyCoord:
        wcs = get_wcs(self.sector, self.camera, self.ccd)
        return wcs.pixel_to_world(self.column, self.row)


class TessCoordList(UserList):
    def __repr__(self):
        x = []
        if len(self) > 8:
            show = [0, 1, 2, 3, -4, -3, -2, -1]
        else:
            show = range(len(self))
        for idx in show:
            x.append(str(self[idx]))
        if len(self) > 8:
            x.insert(4, "...")
        return f"List of {len(self)} coordinates\n ↳[" + "\n   ".join(x) + f"]"

    def to_pandas(self) -> DataFrame:
        data = [
            {
                "sector": c.sector,
                "camera": c.camera,
                "ccd": c.ccd,
                "column": c.column,
                "row": c.row,
            }
            for c in self
        ]
        return DataFrame(data)
