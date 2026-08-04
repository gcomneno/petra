# Phase 1 supported shape domain

> **CONFIDENTIAL — PRIVATE RESEARCH — NOT FOR PUBLIC RELEASE**

## Purpose

Phase 1 proves that a bounded VISION kernel shape can be represented
by canonical geometry and reconstructed exactly from that geometry.

A narrow adapter then proves that the supported native PETRA subset
can enter and leave this kernel without semantic loss.

Phase 1 does not yet address visual style, raster capture, noise,
cryptography, compression, or physical production.

## VISION kernel grammar

The normative Phase 1 semantic domain is:

```text
VisionShape ::= Terminal
              | OrderedGroup(
                    VisionShape[0],
                    ...,
                    VisionShape[n-1]
                )

n >= 1
```

`Terminal` is the unique terminal value.

`OrderedGroup` owns one or more recursively complete child shapes.
Child order is structurally significant.

This is a mathematical value algebra and an implementation boundary.
It is not an additional public PETRA shape model.

## Native PETRA adapter

The supported native PETRA model is projected into the kernel by one
explicit adapter:

```text
adapt(Leaf()) = Terminal

adapt(
    Container(
        Term(Root(0), child[0]),
        ...,
        Term(Root(n-1), child[n-1])
    )
) = OrderedGroup(
    adapt(child[0]),
    ...,
    adapt(child[n-1])
)
```

The reverse adapter reconstructs native PETRA values:

```text
restore(Terminal) = Leaf()

restore(OrderedGroup(child[0], ..., child[n-1])) =
    Container(
        Term(Root(0), restore(child[0])),
        ...,
        Term(Root(n-1), restore(child[n-1]))
    )
```

The PETRA-to-VISION adapter must accept only canonical native shapes.
For every child owned by a native `Term`:

```text
rank(term[i]) = i
```

Root rank is therefore a positional assertion validated at the
adapter boundary, not an independent geometry payload.

For every supported value, the adapter laws are:

```text
restore(adapt(petra_shape)) == petra_shape

adapt(restore(vision_shape)) == vision_shape
```

The adapter must preserve order, must not mutate its input, and must
not attach labels, node IDs, serialized text, or auxiliary metadata.

## Structural facts that geometry must preserve

A conforming Phase 1 geometry must preserve exactly:

1. whether a kernel value is `Terminal` or `OrderedGroup`;
2. the number of children in every ordered group;
3. the left-to-right order of those children;
4. the complete recursively nested shape at every child position;
5. every recursively derived child-index path.

Through the adapter, these facts preserve the corresponding native
PETRA node kind, term count, term order, exponent shapes, and
positional ranks.

## Path correspondence and PETRA address oracle

The geometry core uses only recursively derived child-index paths:

| Kernel concept | Path | Geometric interpretation |
| --- | --- | --- |
| complete shape | `[]` | complete outer geometry |
| first child | `[0]` | first ordered bay |
| nested child | `[0, 2]` | third bay inside the first child |

The decoder must derive every index from spatial order.

For adapter verification, native PETRA addresses provide a reference
oracle:

| PETRA concept | Address | Kernel correspondence |
| --- | --- | --- |
| shape anchor | `@/` | path `[]` |
| first term | `@/0` | child path `[0]` |
| nested term | `@/0/2` | child path `[0, 2]` |
| exponent slot | `@/0/2/^` | child relation at `[0, 2]` |

The geometry core must not call the native address parser or resolver.
Address resolution is a compatibility test performed outside the
encoder and decoder.

Numeric labels, textual rank markers, hidden node IDs, serialized
addresses, or auxiliary ordering tables are forbidden.

## Initial bounded proof corpus

Phase 1 initially supports exhaustive kernel shapes satisfying:

- maximum ordered-group width: `3`;
- maximum structural depth: `3`;
- maximum total kernel shape nodes: `7`;
- every ordered group is non-empty;
- order remains structurally significant.

A mirrored native PETRA corpus is produced with `restore()` and must
contain only canonical root ranks.

The node bound prevents combinatorial explosion while retaining:

- terminal shapes;
- unary nesting;
- sibling order;
- mixed shallow and deep children;
- repeated equal subshapes at distinct positions.

## Explicit exclusions

Phase 1 excludes:

- malformed kernel values;
- malformed or non-canonical PETRA runtime values;
- completion of the overall PETRA roadmap;
- unrelated PETRA utilities not required by the adapter;
- native addresses as an encoder or decoder dependency;
- canonical PETRA serialization as a geometry representation;
- legacy PET numeric projection;
- integer factorisation semantics;
- PETRA rewrite operators;
- raster or photographic decoding;
- geometric error correction;
- secret sharing or encryption;
- aesthetic optimisation;
- physical scale as a security property.

## Exit condition

Phase 1 succeeds only when every bounded kernel shape satisfies:

```text
decode_geometry(encode_geometry(vision_shape)) == vision_shape
```

and every mirrored supported native PETRA shape satisfies:

```text
restore(
    decode_geometry(
        encode_geometry(
            adapt(petra_shape)
        )
    )
) == petra_shape
```

The first law uses kernel structural equality. The second law uses
native PETRA structural equality at the adapter boundary.
