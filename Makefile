.PHONY: clean clean-demo install inplace-install install-venv install-requirements \
	guirc check setupcheck test testall test-coverage lint \
	changelint manualrelease release help

SHELL=/bin/bash

RCC4 = pyrcc4
RCC5 = pyrcc5
PYTHON = /usr/bin/env python

nicos/guisupport/gui_rc_qt4.py: resources/nicos-gui.qrc
	-$(RCC4) -py3 -o $@ $<

nicos/guisupport/gui_rc_qt5.py: resources/nicos-gui.qrc
	-$(RCC5) -o $@ $<

guirc: nicos/guisupport/gui_rc_qt4.py nicos/guisupport/gui_rc_qt5.py

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
	python setup.py install --prefix=$(PREFIX) \
	                        $(and $(DESTDIR),--root=$(DESTDIR))

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
	$(PYTHON) tools/check_setups -s nicos_*/*/setups nicos_*/*/guiconfig.py

T = test

test:
	@if [ -z "`which py.test`" ]; then echo "py.test is required to run the test suite"; exit 1; fi
	@$(PYTHON) `which py.test` -v $(T) --ignore test/test_stresstest $(O)

testall:
	@if [ -z "`which py.test`" ]; then echo "py.test is required to run the test suite"; exit 1; fi
	@$(PYTHON) `which py.test` -v $(T) $(O)

test-coverage:
	@if [ -z "`which py.test`" ]; then echo "py.test is required to run the test suite"; exit 1; fi
	@COVERAGE_PROCESS_START=.coveragerc \
		$(PYTHON) `which py.test` -v $(T) --cov --cov-report=html --cov-report=term $(O)

lint:
	@-PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc nicos/ nicos_*/

changelint:
	PYFILESCHANGED=$$(git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//'  | grep "\.py\$$"); \
	if [[ -n "$$PYFILESCHANGED" ]]; then \
		PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc $$PYFILESCHANGED; \
	else echo 'no python files changed'; fi

manualrelease: test release

release:
	cd doc; rm -rf build/html; ${MAKE} html
	python setup.py sdist

help:
	@echo "Important targets:"
	@echo "  install         - install to $(DESTDIR)$(PREFIX)"
	@echo "  inplace-install - create links from /usr/bin and /etc/init.d to here"
	@echo "  install-venv    - install into a Python virtual environment"
	@echo
	@echo "Development targets:"
	@echo "  clean-demo      - clean up files created by nicos-demo"
	@echo "  setupcheck      - run setup checks"
	@echo "  test            - run test suite"
	@echo "  test-coverage   - run test suite with coverage reporting"
	@echo "  lint            - check source with pylint"
	@echo "  changelint      - check source with pylint (only files in last commit)"
	@echo "  manualrelease   - create tarball for official release (for manual usage)"
	@echo "  release         - create tarball for official release(jenkins usage)"
