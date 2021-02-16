import logging
from pathlib import Path

__version__ = "0.2.1"

__all__ = ["TessCoord", "TessCoordList", "TessImage", "TessImageList", "locate"]

SECTORS = 29

# Where does this package store its embedded data?
PACKAGEDIR: Path = Path(__file__).parent.absolute()
DATADIR: Path = PACKAGEDIR / "data"

# Configure logging
log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())

# Add key objects to the global namespace
from .imagelist import TessImage, TessImageList, list_images  # noqa: E402
from .tesscoord import TessCoord, TessCoordList  # noqa: E402
from .locate import locate  # noqa: E402

__all__ = [
    "TessCoord",
    "TessCoordList",
    "TessImage",
    "TessImageList",
    "locate",
    "list_images",
]
