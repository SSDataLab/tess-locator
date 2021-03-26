from astropy.time import Time
from numpy.testing import assert_array_equal

from tess_locator.time import time_to_sector


def test_time_to_sector():
    # Test single time stamp
    assert time_to_sector("2019-06-01T00:00:00") == [12]
    assert time_to_sector(Time("2019-06-01 00:00:00")) == [12]
    # Test vectorized call
    assert_array_equal(
        time_to_sector(["2018-06-01", "2019-06-01", "2020-06-01"]), [-1, 12, 25]
    )
    assert_array_equal(
        time_to_sector(Time(["2018-06-01", "2019-06-01", "2020-06-01"])), [-1, 12, 25]
    )

    # Sector 1 ended near 2018-08-22 16:07:50
    assert time_to_sector("2018-08-22 16:00:00")[0] == 1
    assert time_to_sector("2018-08-22 17:00:00")[0] == -1

    # Sector 2 started near 2018-08-23 14:28:35
    assert time_to_sector("2018-08-23 14:00:00")[0] == -1
    assert time_to_sector("2018-08-23 15:00:00")[0] == 2
