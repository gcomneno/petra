# PET/PEG 2.0 Graph and Path Traversal

This note defines the first PET/PEG 2.0 graph and path traversal semantics.

The graph layer records possible operator paths through recursive PET object
states:

    object A --operator--> object B --operator--> object C

This layer records alternatives. It does not select a preferred route.

## Graph nodes

A PET/PEG 2.0 graph node wraps one recursive PET object state.

Current implementation:

- `PETGraphNode`
- `PETGraphNode.from_object(obj)`

A node records:

- represented integer value
- PET/PEG 2.0 object payload

Example:

    PETGraphNode(value=60, pet_object=PETObject(60))

## Graph edges

A PET/PEG 2.0 graph edge is one valid operator application between two graph
nodes.

Current implementation:

- `PETGraphEdge`
- `operator_neighbors_by_value(obj)`
- `operator_applications_by_value(obj)`

An edge records:

- source node
- target node
- operator name
- structural address
- optional operator argument
- deterministic label
- full operator application payload

Invalid operator targets are not graph edges.

Example edge:

    60 -- INC(address=[2]) --> 120

## Operator labels

Operator labels are deterministic string labels for graph edges.

Current implementation:

- `operator_label(op, address, argument=None)`

Examples:

    NEW(parent_address=[],q=7)
    DROP(parent_address=[2],p=3)
    INC(address=[2, 2])
    DEC(address=[2])

## One-step graph neighbors

`operator_neighbors_by_value(obj)` emits deterministic valid one-step graph
edges from a PET object.

Example for `PETObject(60)`:

    60 -- NEW(parent_address=[],q=7) --> 420
    60 -- DROP(parent_address=[],p=2) --> 15
    60 -- DROP(parent_address=[],p=3) --> 20
    60 -- DROP(parent_address=[],p=5) --> 12
    60 -- NEW(parent_address=[2],q=3) --> 960
    60 -- DROP(parent_address=[2],p=2) --> 30
    60 -- INC(address=[2]) --> 120
    60 -- DEC(address=[2]) --> 30
    60 -- INC(address=[3]) --> 180
    60 -- INC(address=[5]) --> 300
    60 -- INC(address=[2, 2]) --> 240

Different operators may reach the same target value.

Example:

    DROP(parent_address=[2],p=2) -> 30
    DEC(address=[2])             -> 30

These are distinct graph edges because their operator histories differ.

## Paths

A PET/PEG 2.0 graph path records one concrete operator history.

Current implementation:

- `PETGraphPath`
- `PETGraphPath.root(obj)`
- `PETGraphPath.extend(edge)`

A path records:

- ordered graph nodes
- ordered graph edges
- depth
- value sequence
- operator-label sequence

Example depth-1 path:

    values = [60, 420]
    labels = ["NEW(parent_address=[],q=7)"]

## Path identity and equivalence

Path identity is concrete edge history.

Current implementation:

- `PETGraphPath.identity_key()`
- `path_equivalent(left, right)`

Current identity key uses:

    (source value, operator label, target value)

This means two paths that reach the same final value are not automatically
equivalent.

Example:

    60 -- DROP(parent_address=[2],p=2) --> 30
    60 -- DEC(address=[2])             --> 30

These paths share the same target value but have different path identity.

## Bounded traversal

`traverse_operator_graph_by_value(obj, max_depth, max_paths=None)` performs
deterministic bounded breadth-first traversal.

Current implementation:

- `PETGraphTraversal`
- `traverse_operator_graph_by_value`

Traversal records:

- root node
- maximum depth
- optional maximum emitted path count
- emitted paths
- truncation flag

Depth `0` emits only the root path.

Depth `1` emits the root path and all deterministic one-step neighbor paths.

## Path truncation

Traversal can be explicitly bounded with `max_paths`.

If the traversal reaches the path limit, it returns:

    truncated = True

This is not a routing decision. It is only a bounded traversal constraint.

## Deterministic traversal constraints

Current traversal is deterministic because:

- graph neighbor enumeration is deterministic
- addresses are sorted by address depth and tuple value
- child prime labels are sorted
- traversal is breadth-first
- truncation is based on emitted path count in deterministic order

## Current implementation

Current implementation:

- `src/pet/graph.py`
- `PETGraphNode`
- `PETGraphEdge`
- `PETGraphPath`
- `PETGraphTraversal`
- `operator_label`
- `operator_applications_by_value`
- `operator_neighbors_by_value`
- `path_equivalent`
- `traverse_operator_graph_by_value`

Current tests:

- `tests/test_graph.py`

## Boundary

This semantics does not claim:

- routing-policy promotion
- preferred path selection
- factorization performance
- default CLI behavior changes
- PEG algebra completeness
