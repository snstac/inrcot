# Makefile for Python Programs

.DEFAULT_GOAL := all


all: develop

install_requirements:
	pip install -r requirements.txt

install_requirements_test:
		pip install -r requirements_test.txt

develop: remember
	python setup.py develop

install: remember
	python setup.py install

uninstall:
	pip uninstall -y inrcot

reinstall: uninstall install

remember:
	@echo
	@echo "Hello from the Makefile..."
	@echo "Don't forget to run: 'make install_requirements'"
	@echo

remember_test:
	@echo
	@echo "Hello from the Makefile..."
	@echo "Don't forget to run: 'make install_requirements_test'"
	@echo

clean:
	@rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
		nosetests.xml pylint.log output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log .coverage */__pycache__/

# Publishing:

build: remember_test
	python3 -m build --sdist --wheel

twine_check: remember_test build
	twine check dist/*

upload: remember_test build
	twine upload dist/*

publish: build twine_check upload

# Tests:

pep8: remember_test
	flake8 --max-complexity 12 --exit-zero *.py */*.py

flake8: pep8

lint: remember_test
	pylint --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
	-r n *.py */*.py || exit 0

pylint: lint

pytest: remember_test
	pytest

test: lint pep8 pytest
