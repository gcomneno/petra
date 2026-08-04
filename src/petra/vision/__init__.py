"""Confidential PETRA VISION Phase 1 prototype API."""

from .adapter import (
    adapt_petra_shape,
    restore_petra_shape,
)
from .geometry import (
    Cell,
    GEOMETRY_MALFORMED,
    GeometrySyntaxError,
    OrthogonalGeometry,
    decode_geometry,
    encode_geometry,
    geometry_extent,
    normalize_geometry,
)
from .kernel import (
    OrderedGroup,
    Terminal,
    VisionShape,
    validate_vision_shape,
)

__all__ = [
    "Cell",
    "GEOMETRY_MALFORMED",
    "GeometrySyntaxError",
    "OrderedGroup",
    "OrthogonalGeometry",
    "Terminal",
    "VisionShape",
    "adapt_petra_shape",
    "decode_geometry",
    "encode_geometry",
    "geometry_extent",
    "normalize_geometry",
    "restore_petra_shape",
    "validate_vision_shape",
]
