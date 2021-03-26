from typing import Union, List

from astropy.coordinates import SkyCoord
from astropy.time import Time
import numpy as np

from tess_stars2px import tess_stars2px_function_entry

from . import TessCoord, TessCoordList
from .dates import time_to_sector


def locate(
    target: Union[SkyCoord, str],
    time: Union[Time, str, List[str]] = None,
    sector: Union[int, List[int]] = None,
) -> TessCoordList:
    # Allow the target coordinate to be instantiated from a string
    if isinstance(target, str):
        target = SkyCoord.from_name(target)

    # Allow time to be instantiated from a string
    if time and not isinstance(time, Time):
        time = Time(time)

    # If `time` is given, convert it to a list of sectors
    if time:
        time = np.atleast_1d(time)
        if not target.isscalar and len(target) != len(time):
            raise ValueError("`target` and `time` must have matching lengths")
        sectors_to_search = time_to_sector(time)
    else:
        # Else, ensure `sector` is iterable
        if sector:
            sectors_to_search = np.atleast_1d(sector)
        else:
            sectors_to_search = [None]
        if not target.isscalar and len(target) != len(sectors_to_search):
            raise ValueError("`target` and `sector` must have matching lengths")

    ra = np.atleast_1d(target.ra.to("deg").value)
    dec = np.atleast_1d(target.dec.to("deg").value)
    result = []
    for idx in range(len(ra)):
        (
            _,
            _,
            _,
            out_sector,
            out_camera,
            out_ccd,
            out_col,
            out_row,
            scinfo,
        ) = tess_stars2px_function_entry(
            0, ra[idx], dec[idx], trySector=sectors_to_search[idx]
        )

        for idx_out in range(len(out_sector)):
            if out_sector[idx_out] < 0:
                # tess-point returns -1 if no sector is found
                continue
            try:
                crd = TessCoord(
                    sector=out_sector[idx_out],
                    camera=out_camera[idx_out],
                    ccd=out_ccd[idx_out],
                    column=out_col[idx_out],
                    row=out_row[idx_out],
                )
            except ValueError:
                pass  # illegal column or row, i.e. just off edge
            if time:
                crd.time = time[idx]
            result.append(crd)

    return TessCoordList(result)
