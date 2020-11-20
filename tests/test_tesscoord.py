from astropy.time import Time

from tess_locator import TessCoord


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