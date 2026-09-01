PY ?= python3

.PHONY: install dev test binary release uninstall

install: ## Install `scele` on PATH — same as ./install.sh
	./install.sh

dev: ## Editable install into a local .venv for development
	$(PY) -m venv .venv
	.venv/bin/pip install -e ".[dev,build]"

test:
	.venv/bin/pytest -q

binary: ## Build a standalone binary for this OS/arch into dist/
	./scripts/build-binary.sh

release: ## scripts/release.sh <version>  (bump, commit, tag)
	@test -n "$(VERSION)" || { echo "usage: make release VERSION=0.2.0"; exit 2; }
	./scripts/release.sh $(VERSION)

uninstall:
	./install.sh --uninstall
