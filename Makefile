PYTHON ?= python3
PYTHONPATH := src

.PHONY: test demo docs-check

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests/ -v

demo:
	@set -eu; \
	petra_cli=$$("$(PYTHON)" -c 'import os, sysconfig; print(os.path.join(sysconfig.get_path("scripts"), "petra"))'); \
	shape='1'; \
	invocation='{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}'; \
	if [ ! -x "$$petra_cli" ]; then \
		printf 'FAILED: maintained petra console script not found at %s\n' "$$petra_cli" >&2; \
		false; \
	fi; \
	printf 'PETRA canonical CLI demo\n\n'; \
	printf 'shape = %s\n' "$$shape"; \
	printf 'invocation = %s\n\n' "$$invocation"; \
	"$$petra_cli" "$$shape" "$$invocation"

docs-check:
	$(PYTHON) scripts/check_docs_consistency.py
