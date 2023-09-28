"""TODO:
* Ensure we handle passing a datetime object to `time` gracefully.
* Ensure times during in-between sector gaps don't return results,
e.g. calling locate for `time_to_sector(time=2019-09-12 00:00:00.000, ra=	214.742331, dec=	18.956380)`
should return empty result.
"""
import pytest
from pytest import approx

from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroquery.mast import Tesscut

from tess_locator import locate, SECTORS


def test_pi_men():
    """Tests `locate()` against `astroquery.mast.Tesscut.get_sectors()`"""
    # Query using Tesscut
    crd = SkyCoord(ra=84.291188, dec=-80.46911982, unit="deg")
    mast_result = Tesscut.get_sectors(coordinates=crd)
    # Query using our tool
    our_result = locate(crd)
    # Do the sector, camera, and ccd numbers all match?
    our_result_df = our_result.to_pandas().reset_index()[["sector", "camera", "ccd"]]
    mast_result_df = mast_result.to_pandas().reset_index()[["sector", "camera", "ccd"]]
    # Hack: MAST incorrectly returns Pi Men as having been observed in Sector 35, while in
    # reality it is just off the science area of the CCD, so we ignore the row for Sector 35.
    mast_result_df = mast_result_df.query("sector != 35").reset_index(drop=True)
    # Note: MAST may have less results because it only reports archived data
    assert our_result_df.iloc[0 : len(mast_result_df)].equals(mast_result_df)
    # Can we search by passing a string instead of the coordinates?
    our_result2 = locate("Pi Men")
    assert our_result.to_pandas().round(1).equals(our_result2.to_pandas().round(1))


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
    locate_by_time = (
        locate(crd, time=time).to_pandas().reset_index()[["sector", "camera", "ccd"]]
    )
    locate_by_time_object = (
        locate(crd, time=Time(time))
        .to_pandas()
        .reset_index()[["sector", "camera", "ccd"]]
    )
    locate_by_sector = (
        locate(crd, sector=sector)
        .to_pandas()
        .reset_index()[["sector", "camera", "ccd"]]
    )
    assert locate_by_time.equals(locate_by_sector)
    assert locate_by_time.equals(locate_by_time_object)


def test_locate_time():
    """Ensure a time argument can be passed."""
    crd = SkyCoord(ra=84.291188, dec=-80.46911982, unit="deg")
    assert locate(crd, time="2018-08-01")[0].sector == 1
    assert locate(crd, time=Time("2018-08-01"))[0].sector == 1

    # Ensure time-based location is correct for a known position;
    # the following coordinate is known to have been observed in Sector 17:
    crd = SkyCoord(26.0, 21.0, unit="deg")
    # It cannot have been observed prior to the launch of TESS
    assert len(locate(crd, time="2010-06-01")) == 0
    # It cannot have been observed in 2018
    assert len(locate(crd, time="2018-11-01")) == 0
    # Instead, it was observed during sector 17
    assert len(locate(crd, sector=17)) == 1
    # November 1, 2019, fell during sector 17
    loc = locate(crd, time="2019-11-01")
    assert len(loc) == 1
    assert loc[0].sector == 17
    assert loc[0].camera == 1
    assert loc[0].ccd == 4
    # Can exactly one image be found?
    # images = loc[0].get_images()
    # assert len(images) == 1
    # assert images[0].filename == "tess2019304232925-s0017-1-4-0161-s_ffic.fits"


def test_locate_roundtrip():
    """Is the conversion SkyCoord -> TessCoord -> SkyCoord consistent?"""
    crd1 = SkyCoord.from_name("Proxima Cen")
    crd2 = locate(crd1, aberrate=False)[0].to_skycoord()
    assert approx(crd1.ra.degree) == crd2.ra.degree
    assert approx(crd1.dec.degree) == crd2.dec.degree


def test_edge_case():
    # This coordinate falls just off the edge in Sector 23
    crd = SkyCoord(194.24175295370543, 2.6293646219224858, unit="deg")
    assert len(locate(crd, sector=23)) == 0
