PY ?= python3

.PHONY: install dev test uninstall

install: ## Install `scele` on PATH (Linux/macOS) — same as ./install.sh
	./install.sh

dev: ## Editable install into a local .venv for development
	$(PY) -m venv .venv
	.venv/bin/pip install -e ".[dev]"

test:
	.venv/bin/pytest -q

uninstall:
	./install.sh --uninstall
