.PHONY: build validate test lite
build:
	python scripts/build_catalog.py
	python scripts/generate_jgis.py
	python scripts/validate.py
validate:
	python scripts/validate.py
test:
	python -m pytest -q
lite:
	jupyter lite build --contents content --output-dir dist --XeusAddon.mount_jupyterlite_content=True
