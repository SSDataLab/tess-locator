"""TODO:
Ensure times during in-between sector gaps don't return results,
e.g. calling locate for `time_to_sector(time=2019-09-12 00:00:00.000, ra=	214.742331, dec=	18.956380)`
should return empty result.
"""
from astroquery.mast import Tesscut
from astropy.coordinates import SkyCoord

from tess_locator import locate


def test_pi_men():
    """Tests `locate()` against `astroquery.mast.Tesscut.get_sectors()`"""
    crd = SkyCoord(ra=84.291188, dec=-80.46911982, unit='deg')
    mast_result = Tesscut.get_sectors(crd)
    our_result = locate(crd)
    assert len(mast_result) == len(our_result)
    our_result_df = our_result.to_pandas()[['sector', 'camera', 'ccd']]
    mast_result_df = mast_result[['sector', 'camera', 'ccd']].to_pandas()
    assert our_result_df.equals(mast_result_df)
