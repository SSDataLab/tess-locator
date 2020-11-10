"""Defines the `TessImage` and `TessImageList` classes.

These classes are used to store meta data of Full Frame Images (FFIs).
"""
import io
import re
import warnings
from collections import UserList
from functools import lru_cache
from typing import Union

import attr
import backoff
import httpx
import numpy as np
from astropy.io.fits import HDUList, Header, getheader, open
from astropy.time import Time
from astropy.utils.exceptions import AstropyUserWarning
from astropy.wcs import WCS
from pandas import DataFrame

from . import ffi_catalog, log

FFI_FILENAME_REGEX = r".*-s(\d+)-(\d)-(\d)-.*"
FFI_URL_PREFIX = "https://mast.stsci.edu/portal/Download/file?uri=mast:TESS/product/"


@attr.s(slots=True, frozen=True)
class TessImage:
    filename: str = attr.ib()
    begin: str = attr.ib(default=None)
    end: str = attr.ib(default=None)

    @property
    def sector(self) -> int:
        return int(re.search(FFI_FILENAME_REGEX, self.filename).group(1))

    @property
    def camera(self) -> int:
        return int(re.search(FFI_FILENAME_REGEX, self.filename).group(2))

    @property
    def ccd(self) -> int:
        return int(re.search(FFI_FILENAME_REGEX, self.filename).group(3))

    @property
    def url(self) -> str:
        """Returns the download URL for the image at MAST."""
        return FFI_URL_PREFIX + self.filename

    @lru_cache()
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def download_header(self, ext: int = 1, nbytes: int = 50000) -> Header:
        """Returns the FITS header.

        This method is very fast for the first extension because it will only
        download the first `nbytes` by default.

        Returns
        -------
        header : `astropy.io.fits.header.Header`
        """
        # Download the FFI partially
        http_headers = {}
        if nbytes:
            http_headers["Range"] = f"bytes=0-{nbytes}"
        url = self.url
        log.debug(f"Downloading {nbytes} bytes of {url}")
        resp = httpx.get(url, headers=http_headers)

        # Open the file and extract the fits header
        with warnings.catch_warnings():
            # Ignore "File may have been truncated" warning
            warnings.simplefilter("ignore", AstropyUserWarning)
            hdr = getheader(io.BytesIO(resp.content), ext=ext)
        return hdr

    def download_wcs(self) -> WCS:
        """Downloads the image WCS."""
        return WCS(self.download_header(ext=1, nbytes=40000))

    def download(self) -> HDUList:
        return open(self.url)


class TessImageList(UserList):
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
        return f"List of {len(self)} images\n ↳[" + "\n   ".join(x) + f"]"

    def to_pandas(self) -> DataFrame:
        data = [
            {
                "filename": im.filename,
                "sector": im.sector,
                "camera": im.camera,
                "ccd": im.ccd,
                "begin": im.begin,
                "end": im.end,
                "url": im.url,
            }
            for im in self
        ]
        return DataFrame(data)

    @classmethod
    def from_catalog(cls, catalog: DataFrame):
        # We use raw=True because it gains significant speed
        series = catalog.apply(
            lambda x: TessImage(filename=x[0], begin=x[4], end=x[5]), axis=1, raw=True
        )
        return cls(series.values)


@lru_cache()
def list_images(
    sector: int, camera: int = None, ccd: int = None, time: Union[str, Time] = None
) -> TessImageList:
    df = ffi_catalog.load_ffi_catalog(sector=sector)
    if camera:
        df = df[df.camera == camera]
    if ccd:
        df = df[df.ccd == ccd]
    if time:
        if isinstance(time, str):
            time = Time(time)
        begin = Time(np.array(df.start, dtype=str), format="iso")
        end = Time(np.array(df.stop, dtype=str), format="iso")
        mask = (time >= begin) & (time <= end)
        df = df[mask]
    return TessImageList.from_catalog(df)
