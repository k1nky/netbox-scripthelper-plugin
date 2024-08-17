test:
	python -m unittest discover --verbose tests

coverage:
	python -m coverage run -m unittest discover tests
	python -m coverage html

clean:
	rm -rf build
	rm -rf dist
	rm -rf htmlcov

wheel:
	python3 -m build -w

build: clean wheel

upload:
	twine upload --skip-existing dist/*
