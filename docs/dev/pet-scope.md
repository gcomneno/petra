# PET scope

PET is the artifact, build, validation, and explanation layer.

PET does not perform structural search over opaque integers.

## PET responsibilities

PET is responsible for:

- consuming known factorization or structural payloads
- materializing PET artifacts
- validating support reports
- assembling PET objects
- explaining build results
- standardizing artifact output

## Out of scope

The following concerns are outside PET:

- byte-stream-to-integer discovery
- ISS / IRSR structural search
- root-scale or log-scale search
- candidate-prime discovery
- structural search strategy routing
- claims about reconstructing opaque integers without factorization

Those concerns belong to the dedicated ISS project.

## Correct architecture

ISS / Structural Search
→ structural payload
→ PET Builder
→ PET artifacts

PET starts at the payload/factorization stage.
