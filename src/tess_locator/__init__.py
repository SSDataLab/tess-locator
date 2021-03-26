import logging
from pathlib import Path

__version__ = "0.3.0"

# Where does this package store its embedded data?
from pathlib import Path

PACKAGEDIR: Path = Path(__file__).parent.absolute()
DATADIR: Path = PACKAGEDIR / "data"


# How many sectors are supported in this version?
import tess_stars2px

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
