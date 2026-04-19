# Official showcases

Questa nota raccoglie i due showcase ufficiali del repo.

## 1) Monster spec-driven large build

Obiettivo: mostrare che la pipeline spec-driven può costruire e assemblare un builder molto grande in modo ripetibile.

### Comando

```bash
python tools/pet_big_builder_demo.py \
  --prime-count 2048 \
  --exp 2 \
  --output-dir /tmp/pet_big_builder_demo_2048
```

### Highlight attesi nel summary

```text
schema = pet-big-builder-demo-v1
prime_count = 2048
target_digits = 15373
steps = 4095
build_status = built
assembly_status = assembled
component_count = 2048
```

### Significato operativo

- parte da una factor spec canonica e ripetibile
- attraversa la pipeline builder fino all’oggetto assemblato finale
- dimostra che il collo di bottiglia dei large known builds è stato chiuso nella path spec-driven

---

## 2) Raw hostile exact-built path

Obiettivo: mostrare un percorso completo da intero raw ostile fino a `built-exact-match`, senza usare un factor spec prefornito come input.

### Comando

```bash
python tools/pet_raw_hostile_exact_built_demo.py \
  --output-dir /tmp/pet_raw_hostile_exact_built_demo
```

### Highlight attesi nel summary

```text
schema = pet-raw-hostile-exact-built-demo-v1
input_n = 11413
final_status = built-exact-match
payload_count = 1
candidate_count = 1
attempted_count = 1
built_count = 1
exact_match_count = 1
terminal_status = built
builder_readiness = ready
build_status = built
assembly_status = assembled
known_support = [101, 113]
```

### Significato operativo

- parte dall’intero raw `11413`
- passa per `IRSR -> payload -> builder`
- arriva a un esito esatto e assemblato
- costituisce il proof point concreto di `RAW-TO-BUILDER CLOSED`

---

## Lettura rapida

I due showcase coprono i due fronti chiave:

- **spec-driven monster build**: scala grande e builder assembly
- **raw hostile exact-built**: chiusura end-to-end da input intero ostile
