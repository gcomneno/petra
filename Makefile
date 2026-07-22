PYTHON := python3
PYTHONPATH := src

.PHONY: test demo docs-check

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests/ -v

demo:
	@set -eu; \
	original=72; \
	pet_cli=$$("$(PYTHON)" -c 'import os, sysconfig; print(os.path.join(sysconfig.get_path("scripts"), "pet"))'); \
	pet_file=$$(mktemp "$${TMPDIR:-/tmp}/pet-base-demo.XXXXXX"); \
	trap 'rm -f "$$pet_file"' EXIT HUP INT TERM; \
	printf 'PET-Base demo (N=%s)\n\n' "$$original"; \
	printf '1. Encode canonical JSON\n'; \
	"$$pet_cli" encode "$$original" --json > "$$pet_file"; \
	cat "$$pet_file"; \
	printf '\n2. Show canonical metrics\n'; \
	"$$pet_cli" metrics "$$original"; \
	printf '\n3. Validate encoded artifact\n'; \
	"$$pet_cli" validate "$$pet_file"; \
	printf '\n4. Decode encoded artifact\n'; \
	decoded=$$("$$pet_cli" decode "$$pet_file"); \
	printf '%s\n' "$$decoded"; \
	printf '\n5. Assert roundtrip\n'; \
	if [ "$$decoded" != "$$original" ]; then \
		printf 'FAILED: decoded value %s does not match original N=%s\n' "$$decoded" "$$original" >&2; \
		exit 1; \
	fi; \
	printf 'OK: decoded value matches original N=%s\n' "$$original"

docs-check:
	$(PYTHON) scripts/check_docs_consistency.py
