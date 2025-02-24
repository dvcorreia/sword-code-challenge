format:
	python -m isort .
	python -m black .
	python -m ruff format

test:
	python -m pytest .

coverage:
	python -m coverage erase
	python -m coverage run --source=./clinical_recomendations -m pytest 1> /dev/null
	python -m coverage report

typecheck:
	python -m mypy clinical_recomendations