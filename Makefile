PYTHON := python3
PYTHONPATH := src

.PHONY: test demo docs-check

test:
	PYTHONPATH=$(PYTHONPATH) pytest tests/ -v

demo:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) src/pet.py encode 72
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) src/pet.py encode --json 72

docs-check:
	$(PYTHON) scripts/check_docs_consistency.py
