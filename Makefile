.PHONY: install clean install-inplace test lint jenkinslintall jenkinslint changelint \
	check test-coverage manualrelease release help install-requirements

SHELL=/bin/bash

RCC = pyrcc4
PYTHON = /usr/bin/env python

nicos/guisupport/gui_rc.py: resources/nicos-gui.qrc
	-$(RCC) -py3 -o nicos/guisupport/gui_rc.py resources/nicos-gui.qrc

clean:
	rm -rf build
	find . -name '*.pyc' -print0 | xargs -0 rm -f

clean-demo: clean
	-rm -rf data/cache/*
	-rm -rf data/logbook data/20*
	-rm data/current

install:
	@echo "Installing to $(DESTDIR)$(PREFIX)..."
	@echo
	@if [ -z "$(PREFIX)" ]; then echo "PREFIX is empty! Do not run make install on instruments"; exit 1; fi
	mkdir -p $(DESTDIR)$(PREFIX)
	python setup.py install --prefix=$(DESTDIR)$(PREFIX)

inplace-install:
	-ln -sf -t /etc/init.d $(PWD)/etc/nicos-system
	-ln -sf -t /usr/bin $(PWD)/bin/*

install-venv:
	if [ -z "$(VENVNAME)" ]; then export VENVNAME=nicos-venv ; fi; \
	if [ -z "$(USEPYTHON)" ]; then export USEPYTHON=`which python`; fi; \
	echo "Installing into venv: $(DESTDIR)$${VENVNAME}"; \
	echo "using $${USEPYTHON}"; \
	virtualenv --system-site-packages -p $${USEPYTHON} $(DESTDIR)$${VENVNAME}; \
	. $(DESTDIR)$${VENVNAME}/bin/activate; \
	pip install "pip>=1.5" ; \
	pip install -r requirements.txt ; \
	python setup.py install

install-requirements:
	@echo "Trying to install up-to-date requirements using pip"
	@echo "If something goes wrong, try updating by hand, maybe you need root privileges"
	@echo "Updating pip..."
	pip install "pip>=1.5"
	@echo "Install requirements"
	pip install -r requirements.txt


check:
	$(PYTHON) tools/check_setups $(CHECK_DIRS)

setupcheck:
	$(PYTHON) tools/check_setups -s custom/*/setups

T = test

test:
	@NOSE=`which nosetests`; if [ -z "$$NOSE" ]; then echo "nose is required to run the test suite"; exit 1; fi
	@NOSE_REDNOSE=1 $(PYTHON) `which nosetests` $(T) -v --with-id -e test_stresstest -d --traverse-namespace $(O)

testall:
	@NOSE=`which nosetests`; if [ -z "$$NOSE" ]; then echo "nose is required to run the test suite"; exit 1; fi
	@NOSE_REDNOSE=1 $(PYTHON) `which nosetests` $(T) -v --with-id -d --traverse-namespace $(O)

test-coverage:
	@NOSE=`which nosetests`; if [ -z "$$NOSE" ]; then echo "nose is required to run the test suite"; exit 0; fi
	@COVERAGE_PROCESS_START=.coveragerc NOSE_REDNOSE=1 $(PYTHON) `which nosetests` $(T) -d -v --with-id --with-coverage --cover-package=nicos --traverse-namespace $(O); \
	RESULT=$$?; \
	`which coverage || which python-coverage` html -d cover; \
	echo "nosetest: $$RESULT"; \
	exit $$RESULT

lint:
	@-PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc nicos/ $(shell find custom/ -name \*.py)

jenkinslintall: CUSTOMPYFILES = $(shell find custom/ -name \*.py)
jenkinslintall:
	-PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc --files-output=y nicos/
	-if [[ -n "$(CUSTOMPYFILES)" ]]; then \
		PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc --files-output=y $(CUSTOMPYFILES); \
	else echo 'no custom python files'; fi


jenkinslint:
	-PYFILESCHANGED=$$(git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//' |grep "\.py\$$"); \
	if [[ -n "$$PYFILESCHANGED" ]] ; then \
		PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc --files-output=y $$PYFILESCHANGED; \
	else echo 'no python files changed'; fi

changelint:
	PYFILESCHANGED=$$(git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//'  | grep "\.py\$$"); \
	if [[ -n "$$PYFILESCHANGED" ]]; then \
		PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc $$PYFILESCHANGED; \
	else echo 'no python files changed'; fi

manualrelease: test release

release:
	cd doc; rm -r build/html; ${MAKE} html
	python setup.py sdist

help:
	@echo "Important targets:"
	@echo "  install-inplace - build everything for running NICOS from here"
	@echo
	@echo "Development targets:"
	@echo "  setupcheck      - run setup checks"
	@echo "  test            - run test suite"
	@echo "  test-coverage   - run test suite with coverage reporting"
	@echo "  lint            - check source with pylint"
	@echo "  changelint      - check source with pylint (only files in last commit)"
	@echo "  manualrelease   - create tarball for official release (for manual usage)"
	@echo "  release         - create tarball for official release(jenkins usage)"
