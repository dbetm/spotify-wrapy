install:
	@( \
		. .venv/bin/activate; \
		pip install -r requirements.txt; \
	)


dev-setup:
	@( \
		. .venv/bin/activate; \
		pip install -r requirements-dev.txt; \
	)


format-preview:
	@( \
		isort --check-only .; \
	)

format-apply:
	@( \
		isort .; \
	)