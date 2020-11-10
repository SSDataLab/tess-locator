__version__ = "0.1.3"

__all__ = ["TessCoord", "TessCoordList", "TessImage", "TessImageList", "locate"]

SECTORS = 28

# Where does this package store its embedded data?
from pathlib import Path

PACKAGEDIR = Path(__file__).parent.absolute()
DATADIR = PACKAGEDIR / "data"

# Configure logging
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

# Add key objects to the global namespace
from .imagelist import TessImage, TessImageList, list_images
from .tesscoord import TessCoord, TessCoordList
from .locate import locate
