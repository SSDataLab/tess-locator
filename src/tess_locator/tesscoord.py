from collections import UserList
from typing import Union

import attr
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord
from pandas import DataFrame

# The science area of the TESS CCDs are bounded by:
# lower left corner: (column, row) = (45, 1)
# upper right corner: (column, row) = (2092, 2048)
# By convention, the pixel coordinates refer to the centers of pixels,
# so the valid ranges are:
COLUMN_RANGE = [44.5, 2092.5]
ROW_RANGE = [0.5, 2048.5]


def _optional_time_converter(time) -> Time:
    return Time(time) if time else None


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
    time: Time = attr.ib(
        converter=_optional_time_converter,
        repr=lambda value: f"{value.iso[:19]}" if value else "None",
        default=None,
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

    def to_skycoord(self) -> SkyCoord:
        """Convert the TESS coordinate to an (ra, dec) sky coordinate."""
        from tess_stars2px import tess_stars2px_reverse_function_entry

        ra, dec, scinfo = tess_stars2px_reverse_function_entry(
            self.sector, self.camera, self.ccd, self.column, self.row
        )
        crd = SkyCoord(ra, dec, unit="deg")
        crd.obstime = self.time
        return crd

    def list_images(self, time: Union[str, Time] = None, author: str = "spoc"):
        """Returns a `TessImageList` detailing the FFI images which include the coordinate.

        Parameters
        ----------
        author : str
            "spoc" or "tica"

        Notes
        -----
        This feature will use the `tess-cloud` package to query a catalog of
        TESS images.
        """
        # local import to avoid circular dependency
        from tess_cloud import list_images

        if time is None:
            time = self.time
        return list_images(
            sector=self.sector,
            camera=self.camera,
            ccd=self.ccd,
            time=time,
            author=author,
        )


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
        return f"List of {len(self)} coordinates\n ↳[" + "\n   ".join(x) + "]"

    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and self.to_pandas().equals(
            obj.to_pandas()
        )

    def list_images(self, time: Union[str, Time] = None, author: str = "spoc"):
        """Returns a `TessImageList` detailing the FFI images which include the coordinates.

        Parameters
        ----------
        author : str
            "spoc" or "tica"
        """
        # local import to avoid circular dependency
        from tess_cloud import TessImageList

        if len(self) == 0:
            return TessImageList([])

        result = self[0].list_images(time=time, author=author).copy()
        for img in self[1:]:
            result += img.list_images(time=time, author=author)
        return result

    def to_pandas(self) -> DataFrame:
        data = {
            "sector": [c.sector for c in self],
            "camera": [c.camera for c in self],
            "ccd": [c.ccd for c in self],
            "column": [c.column for c in self],
            "row": [c.row for c in self],
            "time": [c.time for c in self],
        }
        return DataFrame(data).set_index("time")

    @classmethod
    def from_pandas(cls, df: DataFrame):
        if "time" not in df.columns:
            df.loc[:, "time"] = df.index
        series = df.apply(
            lambda x: TessCoord(
                sector=x.sector,
                camera=x.camera,
                ccd=x.ccd,
                column=x.column,
                row=x.row,
                time=x.time,
            ),
            axis=1,
        )
        return cls(series.values)
