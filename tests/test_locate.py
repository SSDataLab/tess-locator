"""TODO:
* Ensure we handle passing a datetime object to `time` gracefully.
* Ensure times during in-between sector gaps don't return results,
e.g. calling locate for `time_to_sector(time=2019-09-12 00:00:00.000, ra=	214.742331, dec=	18.956380)`
should return empty result.
"""
import pytest
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroquery.mast import Tesscut

from tess_locator import locate


def test_pi_men():
    """Tests `locate()` against `astroquery.mast.Tesscut.get_sectors()`"""
    # Query using Tesscut
    crd = SkyCoord(ra=84.291188, dec=-80.46911982, unit="deg")
    mast_result = Tesscut.get_sectors(crd)
    # Query using our tool
    our_result = locate(crd)
    # Do we get the same number of results?
    assert len(mast_result) == len(our_result)
    # Do the sector, camera, and ccd numbers all match?
    our_result_df = our_result.to_pandas()[["sector", "camera", "ccd"]]
    mast_result_df = mast_result[["sector", "camera", "ccd"]].to_pandas()
    assert our_result_df.equals(mast_result_df)
    # Can we search by passing a string instead of the coordinates?
    our_result2 = locate("Pi Men")
    assert our_result == our_result2


def test_scalar_vs_nonscalar_coordinate():
    """Does a scalar vs a non-scalar SkyCoord return the same result?"""
    crd1 = SkyCoord(ra=84.291188, dec=-80.46911982, unit="deg")
    crd2 = SkyCoord(ra=[84.291188], dec=[-80.46911982], unit="deg")
    assert locate(crd1) == locate(crd2)


def test_scalar_arguments():
    # Can we obtain the location of Pi Men in 3 sectors in one call?
    ra = [84.291188, 84.291188, 84.291188]
    dec = [-80.46911982, -80.46911982, -80.46911982]
    time = ["2018-08-01", "2019-05-01", "2019-06-01"]
    sector = [1, 11, 12]
    crd = SkyCoord(ra=ra, dec=dec, unit="deg")

    # crd and time/sector must have matching lengths
    with pytest.raises(ValueError, match="matching lengths"):
        locate(crd)
    with pytest.raises(ValueError, match="matching lengths"):
        locate(crd, time=time[:2])
    with pytest.raises(ValueError, match="matching lengths"):
        locate(crd, sector=sector[:2])

    # Do we recover the correct results?
    assert locate(crd, time=time) == locate(crd, sector=sector)
    assert [tesscoord.sector for tesscoord in locate(crd, time=time)] == sector
    # Can time be a Time object?
    assert locate(crd, time=Time(time)) == locate(crd, sector=sector)


def test_locate_time():
    """Ensure a time argument can be passed."""
    crd = SkyCoord(ra=84.291188, dec=-80.46911982, unit="deg")
    assert locate(crd, time="2018-08-01")[0].sector == 1
    assert locate(crd, time=Time("2018-08-01"))[0].sector == 1
