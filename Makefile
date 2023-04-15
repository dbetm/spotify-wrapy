install:
	@( \
		. .venv/bin/activate; \
		pip install -r requirements.txt; \
	)


dev-install:
	@( \
		. .venv/bin/activate; \
		pip install -r requirements-dev.txt; \
	)


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