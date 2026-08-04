# Phase 1 minimal geometric grammar

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Status

This is a proof grammar.

It is not asserted to be the final PETRA VISION visual language and
is not, by itself, a statement of patent scope.

## Design principle

No complete supported structural payload may accompany the
geometry as an auxiliary decoding channel.

The spatial construction must carry:

- node kind;
- child count;
- child order;
- recursive containment;
- positional traversal.

## Primitive vocabulary

Phase 1 uses an integer orthogonal lattice and three geometric
concepts.

### Terminal cell

A terminal cell is one canonical solid unit square.

It represents exactly one kernel `Terminal`.

### Container frame

A container frame is a canonical hollow orthogonal boundary
containing one or more ordered bays.

It represents one kernel `OrderedGroup`.

### Ordered bay

A bay is one geometrically delimited interior region of a container
frame.

Each bay represents one ordered child position.

The bay interior contains exactly one recursively encoded child
geometry. Through the PETRA adapter, this region corresponds to a
term's exponent slot.

## Kernel semantic mapping

| VISION kernel value | Geometric embodiment |
| --- | --- |
| `Terminal` | one solid terminal cell |
| `OrderedGroup(...)` | one hollow container frame |
| child position `i` | ordered bay `i` |
| child shape | nested geometry inside bay `i` |

## Native PETRA adapter projection

| Native PETRA value | Kernel projection |
| --- | --- |
| `Leaf()` | `Terminal` |
| `Container(...)` | `OrderedGroup(...)` |
| `Term` at position `i` | child position `i` |
| `Root(rank=i)` | positional assertion for child `i` |
| exponent shape | child shape |

No glyph is allocated specifically to `Root`.

The adapter validates root ranks before encoding and reconstructs
them by enumerating decoded child positions from left to right.

The geometry core must not import or call canonical PETRA
serialization, address resolution, rewrite operators, or legacy PET
numeric machinery.

## Canonical coordinate rules

All canonical coordinates are integers.

Every encoded geometry is translated so that its minimum coordinate
is the origin.

### Terminal extent

A terminal cell occupies the unit bounding box:

```text
width  = 1
height = 1
```

### Child clearance

Every child geometry is surrounded by a one-unit interior
clearance from its bay boundary.

This clearance belongs to grammar syntax and is not optional visual
decoration.

### Bay placement

Bays are placed from left to right in kernel child order.

Consecutive bays are separated by one complete orthogonal separator.

Canonical geometry is an occupied-cell set represented by a sorted tuple.
Source-layer identity and overlapping identical drawings are not represented:
drawing the same child twice at identical coordinates adds no observable
geometry.

### Container extent

The container frame is the smallest canonical frame that encloses:

- every bay;
- every separator;
- the required child clearances.

Its dimensions are derived exclusively from the canonical child
bounding boxes.

### Vertical alignment

For a container of height `H`, every child maximum y-coordinate is `H - 3`.
Children therefore share the same canonical upper alignment. A shorter child
leaves unused space only toward smaller y-coordinates; children are not
vertically centred.

No renderer-dependent centring or alignment is permitted.

## Recursive encoder

Conceptually:

```text
encode(Terminal):
    return terminal_cell()

encode(OrderedGroup(children)):
    encoded_children = [encode(child) for child in children]
    bays = place_in_order(encoded_children)
    return minimal_container_frame(bays)
```

The encoder validates only the bounded VISION kernel contract.

Native PETRA validation and conversion occur before core encoding in
the adapter layer.

## Recursive decoder

Conceptually:

```text
decode(geometry):
    geometry = canonical_normalise(geometry)

    if geometry is exactly one terminal cell:
        return Terminal

    frame = parse_container_frame(geometry)
    bays = parse_ordered_bays(frame)

    children = [
        decode(extract_child_geometry(bay))
        for bay in bays
    ]

    return OrderedGroup(children)
```

The geometry decoder returns a VISION kernel value.

A separate native PETRA adapter may then reconstruct `Leaf`,
`Container`, `Term`, and canonical `Root` values from that kernel
value.

The decoder receives no external rank list, node table, address list,
serialized PETRA value, adapter-side state, or hidden payload.

## Canonical normalisation

Phase 1 permits only translation normalisation.

Translating the complete occupied-cell set by one uniform offset is accepted
and normalised. Translation is malformed only when it affects part of the
geometry, uses different offsets for different regions, or leaves residual
cells from the pre-translation record.

Rotation, reflection, non-uniform scaling, arbitrary resizing, and
free-form deformation are not equivalent transformations during the
initial proof.

This deliberately removes symmetry ambiguity from the first
implementation.

## Required geometric distinctions

The grammar must make these kernel cases distinct without labels:

```text
Terminal

OrderedGroup(Terminal)

OrderedGroup(Terminal, Terminal)

OrderedGroup(OrderedGroup(Terminal))

OrderedGroup(Terminal, OrderedGroup(Terminal))

OrderedGroup(OrderedGroup(Terminal), Terminal)
```

In particular, exchanging two ordered bays must produce a different
canonical geometry whenever their child shapes differ.

Exchanging two distinct complete canonical bay regions is a valid semantic
permutation: it is the canonical geometry of a different `OrderedGroup`.
It is not a malformed geometry case. In contrast, transplanting child payload
cells into fixed incompatible bay extents without rebuilding the canonical
parent geometry is malformed.

## Rejection rules

The decoder must reject geometry containing:

- neither a valid terminal cell nor a valid container frame;
- an empty container frame;
- missing or partial separators;
- a payload intrusion or bridge through required clearance across a
  separator;
- two distinct disconnected child components in one bay;
- no child geometry inside a bay;
- a child whose occupied cells cross a separator or bay boundary;
- non-canonical clearance;
- trailing primitives outside the outer frame;
- ambiguous terminal-versus-container topology.

Here, a child crosses a separator or boundary only when its occupied cells
intrude through the required clearance into those cells or into another bay;
it does not refer to source-object identity.

### Representation boundary

`OrthogonalGeometry` construction or trusted-record revalidation handles
non-tuple records, malformed cells, non-exact integer coordinates,
noncanonical tuple ordering, and duplicate cell entries. These are
representation-boundary failures, distinct from mutations that successfully
construct a record and then reach `decode_geometry`. Constructor failures
retain their `TypeError` or `ValueError` contracts; they are not necessarily
`GeometrySyntaxError`.

## Non-reliance rule

Colour, textual labels, filenames, drawing order, object IDs,
metadata, SVG element names, CSS classes, adapter-side state, and
source-code object identity must not affect decoding.

Only canonical geometry and the fixed kernel grammar may determine
the reconstructed VISION shape.

## Decoder resource boundary

The finite structural domain gives this grammar a finite canonical geometric
envelope. Across the complete 110-shape Phase 1 corpus, the largest valid
canonical record has:

- at most `181` occupied cells;
- bounding width at most `25` cells;
- bounding height at most `13` cells.

The decoder checks all three limits before it constructs a frame perimeter,
iterates over a bounding width or height, or creates a bounding-box-scale
collection. It also accepts coordinates only when each exact integer has
magnitude at most `2^63 - 1`. This finite coordinate-resource rule still
allows ordinary translated canonical geometries; translation remains the only
normalisation and is not otherwise weakened.

An over-budget or otherwise malformed `OrthogonalGeometry` record that
reaches decoding fails with `GeometrySyntaxError` containing
`GEOMETRY_MALFORMED`. A resource-envelope violation is a malformed decoder
case, not a separate successful interpretation.

At construction, `OrthogonalGeometry` snapshots a tuple subclass used for
the outer cell record or an individual cell into exact built-in tuples.
Therefore later mutable tuple-subclass behaviour cannot influence validation
or decoding.
