# petraw-v0

`petraw-v0` è il formato binario canonico per serializzare una shape PET ottenuta
da una sorgente di byte arbitraria tramite il codec PET-native di riferimento.

## Scopo

Questo formato non è definito come compressore generale.
Lo scopo è:

- rappresentare in modo deterministico una shape PET costruita da dati arbitrari
- permettere roundtrip esatto `bytes -> PET shape -> bytes`
- fornire un contenitore binario minimale e stabile per la shape

## Pipeline canonica

La pipeline di riferimento è:

1. input bytes
2. `encode_bytes(data)` -> shape PET-native
3. `shape_to_raw_bytes(shape)` -> `petraw-v0`

Il decoding canonico è:

1. `shape_from_raw_bytes(blob)` -> shape
2. `decode_shape(shape)` -> bytes originali

## Header

Il file `petraw-v0` inizia con un header fisso di 5 byte:

- magic ASCII: `PTRW`
- version byte: `0`

Quindi:

- byte 0..3: `50 54 52 57` (`PTRW`)
- byte 4: `00`

## Payload

Dopo l'header, il payload è una serializzazione preorder della shape.

Ogni nodo è codificato come:

- `uvarint(arity(node))`
- poi ricorsivamente i suoi `arity(node)` figli, in ordine canonico

Dove:

- una foglia `()` ha arità `0`
- un nodo con `k` figli ha arità `k`

## Esempi concettuali

- `()` -> `uvarint(0)`
- `((),)` -> `uvarint(1), uvarint(0)`
- `((),())` -> `uvarint(2), uvarint(0), uvarint(0)`

Questi esempi descrivono solo il payload.
Nel file reale vanno preceduti da header `PTRW` + versione `0`.

## Uvarint

Gli interi non negativi sono codificati come unsigned varint base-128:

- 7 bit di payload per byte
- bit alto `1` = continuazione
- bit alto `0` = ultimo byte

## Canonicalità

La canonicalità della shape non è imposta dal contenitore binario in sé,
ma dalla pipeline che produce la shape PET-native.

Il formato `petraw-v0` serializza una shape già costruita/normalizzata
dall'implementazione di riferimento.

## Errori di parsing

Un decoder `petraw-v0` deve rifiutare almeno i seguenti casi:

- header troppo corto
- magic diversa da `PTRW`
- versione non supportata
- uvarint troncato
- byte residui dopo il parsing completo della shape

## Proprietà garantite dall'implementazione di riferimento

L'implementazione di riferimento in `tools/bytes_to_pet_shape.py` garantisce:

- determinismo del mapping `bytes -> shape`
- roundtrip esatto `bytes -> shape -> bytes`
- serializzazione binaria `petraw-v0`
- parsing robusto del formato con validazione header/payload

## Comandi di riferimento

```bash
python tools/bytes_to_pet_shape.py encode INPUT.bin --roundtrip-check
python tools/bytes_to_pet_shape.py encode-raw INPUT.bin --out OUTPUT.petraw
python tools/bytes_to_pet_shape.py decode-raw OUTPUT.petraw --out RESTORED.bin
```

Stato epistemico

petraw-v0 va inteso come:

formato canonico della rappresentazione PET dei dati nel prototipo corrente
non come formato di compressione ottimale
non come sostituto di gzip/xz/zstd
