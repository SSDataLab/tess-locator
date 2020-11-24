from astropy.time import Time
import pandas as pd

from tess_locator import TessCoord, TessCoordList


def test_time_support():
    # Can time be passed as a string?
    time = "2018-08-01"
    tc = TessCoord(1, 1, 1, 100, 100, time=time)
    assert isinstance(tc.time, Time)
    assert tc.to_skycoord().obstime == time
    # Can time be passed as Time object?
    time = Time("2018-08-01")
    tc = TessCoord(1, 1, 1, 100, 100, time=time)
    assert tc.to_skycoord().obstime == time
    # Cna time be None?
    time = None
    tc = TessCoord(1, 1, 1, 100, 100, time=time)
    assert tc.to_skycoord().obstime is None


def test_empty_list():
    """Does to_pandas() on an empty list still contain the expected columns?"""
    empty = TessCoordList([])
    assert len(empty) == 0
    df = empty.to_pandas()
    assert "sector" in df.columns
    assert "camera" in df.columns
    assert "ccd" in df.columns


def test_list_from_pandas():
    """Tests the `TessCoordList.from_pandas()` feature."""
    df = pd.DataFrame(
        {
            "sector": [1, 2],
            "camera": [3, 4],
            "ccd": [1, 2],
            "column": [100, 200],
            "row": [300, 400],
            "time": ["2019-01-01", "2019-01-02"],
        },
    )
    coordlist = TessCoordList.from_pandas(df)
    assert coordlist[0].sector == 1
    assert coordlist[1].time == "2019-01-02"
    coordlist.to_pandas().equals(df)  # Can we roundtrip?
