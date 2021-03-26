from astropy.time import Time
import pandas as pd
import numpy as np

from . import DATADIR


def time_to_sector(time: Time):
    """Returns the sector number for a given timestamp.
    Returns -1 otherwise.
    """
    if isinstance(time, Time):
        time = time.iso
    time_input = pd.DataFrame(np.atleast_1d(time))

    sector_dates = get_sector_dates()
    sectors = time_input.apply(
        lambda t: sector_dates.index.values[
            (sector_dates.begin.values <= t.values)
            & (sector_dates.end.values >= t.values)
        ],
        axis=1,
    )
    # There should be one sector result per row; return -1 otherwise
    result = sectors.apply(lambda s: s[0] if len(s) > 0 else -1)
    return result.values


def get_sector_dates():
    return pd.read_csv(DATADIR / "tess-sector-dates.csv", index_col="sector")
