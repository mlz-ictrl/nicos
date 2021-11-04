.PHONY: clean clean-demo install inplace-install install-venv install-requirements \
	guirc check setupcheck test testall test-coverage lint \
	changelint manualrelease release help

PODMAN_OR_DOCKER = $(shell which podman || which docker || \
                     echo podman_or_docker 2>/dev/null)

SHELL=/bin/bash

RCC5 = pyrcc5
PYTHON = /usr/bin/env python3

nicos/guisupport/gui_rc_qt5.py: resources/nicos-gui.qrc
	-$(RCC5) -o $@ $<

guirc: nicos/guisupport/gui_rc_qt5.py

pod-demo:
	$(PODMAN_OR_DOCKER) run -u `id -u` -v `pwd`:/nicos -p 1301:1301 \
	--rm -it quay.io/cfelder/nicos:latest

clean:
	rm -rf build
	find . -name '__pycache__' -exec rm -rf {} \;
	rm -rf test/root/

clean-demo: clean
	-rm -rf data/cache/*
	-rm -rf data/logbook data/20*
	-rm -rf log/poller* log/cache log/daemon log/elog log/nicos log/watchdog
	-rm data/current

install:
	@echo "Installing to $(DESTDIR)$(PREFIX)..."
	@echo
	@if [ -z "$(PREFIX)" ]; then echo "PREFIX is empty! Do not run make install on instruments"; exit 1; fi
	mkdir -p $(DESTDIR)$(PREFIX)
	$(PYTHON) setup.py install --prefix=$(PREFIX) \
	                        $(and $(DESTDIR),--root=$(DESTDIR)) \
				$(and $(INSTRUMENT),--instrument=$(INSTRUMENT)) \
				$(and $(SETUPPACKAGE), --setup-package=$(SETUPPACKAGE))

inplace-install:
	-ln -sf -t /etc/init.d "$$(pwd)/etc/nicos-system"
	-ln -sf -t /usr/bin "$$(pwd)"/bin/*

install-venv:
	if [ -z "$(VENVNAME)" ]; then export VENVNAME=nicos-venv ; fi; \
	if [ -z "$(USEPYTHON)" ]; then export USEPYTHON=`which python3`; fi; \
	echo "Installing into venv: $(DESTDIR)$${VENVNAME}"; \
	echo "using $${USEPYTHON}"; \
	$${USEPYTHON} -m venv --copies --system-site-packages $(DESTDIR)$${VENVNAME}; \
	. $(DESTDIR)$${VENVNAME}/bin/activate; \
	pip install -U pip ; \
	pip install -r requirements.txt ; \
	python setup.py install

install-requirements:
	@echo "Trying to install up-to-date requirements using pip"
	@echo "If something goes wrong, try updating by hand, maybe you need root privileges"
	@echo "Updating pip..."
	pip install -U pip
	@echo "Install requirements"
	pip install -r requirements.txt


check:
	$(PYTHON) tools/check-setups $(CHECK_DIRS)

setupcheck:
	$(PYTHON) tools/check-setups -s nicos_*/*/setups nicos_*/*/guiconfig.py

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
	@-PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc nicos/ nicos_*/ nicostools/ tools/* bin/*

changelint:
	PYFILESCHANGED=$$(git diff --name-only --diff-filter=dux HEAD^...HEAD | grep "\.py$$" | grep -v setups) ; \
	if [[ -n "$$PYFILESCHANGED" ]]; then \
		PYTHONPATH=.:${PYTHONPATH} pylint --rcfile=./pylintrc $$PYFILESCHANGED; \
	else echo 'no python files changed'; fi

manualrelease: test release

release:
	cd doc; rm -rf build/html; ${MAKE} html
	$(PYTHON) setup.py sdist

help:
	@echo "Important targets:"
	@echo "  install         - install to $(DESTDIR)$(PREFIX)"
	@echo "  inplace-install - create links from /usr/bin and /etc/init.d to here"
	@echo "  install-venv    - install into a Python virtual environment"
	@echo
	@echo "Development targets:"
	@echo "  pod-demo        - start nicos-demo pod using podman or docker"
	@echo "  clean-demo      - clean up files created by nicos-demo"
	@echo "  setupcheck      - run setup checks"
	@echo "  test            - run test suite"
	@echo "  test-coverage   - run test suite with coverage reporting"
	@echo "  lint            - check source with pylint"
	@echo "  changelint      - check source with pylint (only files in last commit)"
	@echo "  manualrelease   - create tarball for official release (for manual usage)"
	@echo "  release         - create tarball for official release(jenkins usage)"
