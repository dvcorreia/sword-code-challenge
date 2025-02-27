.PHONY: rules
rules:
	opa build -b rules/ --ignore "*_test.rego" -o rules/bundle.tar.gz
rules.test:
	opa test rules/ -v

format:
	python -m isort .
	python -m black .
	python -m ruff format

test:
	python -m pytest .

coverage:
	python -m coverage erase
	python -m coverage run --source=./clinical_recommendations -m pytest 1> /dev/null
	python -m coverage report

typecheck:
	python -m mypy clinical_recommendations