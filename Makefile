gen:
	sqlc generate -f clinical_recommendations/storage/sqlc.yaml

.PHONY: rules
rules:
	opa build -b rules/ --ignore "*_test.rego" -o rules/bundle.tar.gz
rules.eval:
	curl localhost:8181/v1/data/clinical_recommendations/rules/recommendations -d @misc/opa-input.json -H 'Content-Type: application/json'
rules.test:
	opa test rules/ -v

format:
	python -m isort .
	python -m black .
	python -m ruff check --fix

test:
	python -m pytest .

coverage:
	python -m coverage erase
	python -m coverage run --source=./clinical_recommendations -m pytest 1> /dev/null
	python -m coverage report

typecheck:
	python -m mypy clinical_recommendations