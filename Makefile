SHELL=/bin/bash


install:
	@[ ! -d .venv ] && python3 -m venv .venv ||:;
	@( \
		source .venv/bin/activate || exit 1; \
		pip install -r requirements.txt || exit 1; \
	)


dev-install:
	@[ ! -d .venv ] && python3 -m venv .venv ||:;
	@( \
		source .venv/bin/activate || exit 1; \
		pip install -r requirements-dev.txt || exit 1; \
	)


full-install: install dev-install


format-preview:
	@( \
		isort --check-only .; \
		black --check .; \
	)


format-apply:
	@( \
		isort .; \
		black .; \
	)