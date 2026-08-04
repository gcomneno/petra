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
    PHASE_1_MAX_COORDINATE_MAGNITUDE,
    PHASE_1_MAX_GEOMETRY_CELLS,
    PHASE_1_MAX_GEOMETRY_HEIGHT,
    PHASE_1_MAX_GEOMETRY_WIDTH,
    decode_geometry,
    encode_geometry,
    geometry_extent,
    normalize_geometry,
)
from .kernel import (
    OrderedGroup,
    PHASE_1_MAX_ORDERED_GROUP_WIDTH,
    PHASE_1_MAX_STRUCTURAL_DEPTH,
    PHASE_1_MAX_TOTAL_NODES,
    Terminal,
    VisionShape,
    VISION_SHAPE_OUT_OF_BOUNDS,
    validate_vision_shape,
)

__all__ = [
    "Cell",
    "GEOMETRY_MALFORMED",
    "GeometrySyntaxError",
    "OrderedGroup",
    "OrthogonalGeometry",
    "PHASE_1_MAX_COORDINATE_MAGNITUDE",
    "PHASE_1_MAX_GEOMETRY_CELLS",
    "PHASE_1_MAX_GEOMETRY_HEIGHT",
    "PHASE_1_MAX_GEOMETRY_WIDTH",
    "PHASE_1_MAX_ORDERED_GROUP_WIDTH",
    "PHASE_1_MAX_STRUCTURAL_DEPTH",
    "PHASE_1_MAX_TOTAL_NODES",
    "Terminal",
    "VisionShape",
    "VISION_SHAPE_OUT_OF_BOUNDS",
    "adapt_petra_shape",
    "decode_geometry",
    "encode_geometry",
    "geometry_extent",
    "normalize_geometry",
    "restore_petra_shape",
    "validate_vision_shape",
]
