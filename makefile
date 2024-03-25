mypy:
	echo "Running mypy"
	MYPYPATH=src mypy .

tests:
	echo "Running tests"
	pytest test/
