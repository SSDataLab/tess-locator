import logging
from pathlib import Path
import tess_stars2px  # provided by the `tess-point` package

__version__ = "0.4.1"

# Where does this package store its embedded data?
PACKAGEDIR: Path = Path(__file__).parent.absolute()
DATADIR: Path = PACKAGEDIR / "data"

# How many sectors are supported in this version?
SECTORS = tess_stars2px.TESS_Spacecraft_Pointing_Data.sectors[-1]

# Configure logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

# Add key objects to the global namespace
from .tesscoord import TessCoord, TessCoordList  # noqa: E402
from .locate import locate  # noqa: E402

__all__ = [
    "TessCoord",
    "TessCoordList",
    "locate",
]
