.PHONY: all gui install clean inplace test lint jenkinslintall jenkinslint changelint \
	check test-coverage install main-install install-gui main-install-gui release \
	fixsmb help custom-all custom-inplace custom-install custom-clean custom-gui

SHELL=/bin/bash

RCC = pyrcc4
PYTHON = /usr/bin/env python

all:
	$(PYTHON) setup.py $(QOPT) build -e "/usr/bin/env python"
	$(PYTHON) etc/set_version.py build/lib*
	-${MAKE} custom-all

gui: lib/nicos/guisupport/gui_rc.py
	$(PYTHON) setup.py $(QOPT) build -e "/usr/bin/env python"
	$(PYTHON) etc/set_version.py build/lib*
	-${MAKE} custom-gui

lib/nicos/guisupport/gui_rc.py: resources/nicos-gui.qrc
	-$(RCC) -o lib/nicos/guisupport/gui_rc.py resources/nicos-gui.qrc

clean-backups:
	@if [[ -e "$(ROOTDIR)/bin.bak" ]]; then rm -rI "$(ROOTDIR)/bin.bak"; fi
	@if [[ -e "$(ROOTDIR)/lib.bak" ]]; then rm -rI "$(ROOTDIR)/lib.bak"; fi
	@if [[ -e "$(ROOTDIR)/bin.bak.~1~" ]]; then\
		 rm -rf $(ROOTDIR)/bin.bak.~*~; fi
	@if [[ -e "$(ROOTDIR)/lib.bak.~1~" ]]; then\
		 rm -rf $(ROOTDIR)/lib.bak.~*~; fi

clean:
	rm -rf build
	find . -name '*.pyc' -print0 | xargs -0 rm -f
	-${MAKE} custom-clean

clean-demo: clean
	-rm -rf data/cache/*
	-rm -rf data/logbook data/20*
	-rm data/current

inplace:
	rm -rf build
	$(PYTHON) setup.py $(QOPT) build_ext
	cp build/lib*/nicos/services/daemon/*.so lib/nicos/services/daemon
	-${MAKE} custom-inplace


LIVEWIDGET_DEPS=src/livewidget/livewidget.pro \
src/livewidget/lw_common.h \
src/livewidget/lw_controls.cpp \
src/livewidget/lw_controls.h \
src/livewidget/lw_data.cpp \
src/livewidget/lw_data.h \
src/livewidget/lw_histogram.cpp \
src/livewidget/lw_histogram.h \
src/livewidget/lw_imageproc.cpp \
src/livewidget/lw_imageproc.h \
src/livewidget/lw_main.cpp \
src/livewidget/lw_plot.cpp \
src/livewidget/lw_plot.h \
src/livewidget/lw_profile.cpp \
src/livewidget/lw_profile.h \
src/livewidget/lw_widget.cpp \
src/livewidget/lw_widget.h \
src/livewidget/python/configure.py


src/livewidget/python/livewidget.so: $(LIVEWIDGET_DEPS)
	cd src/livewidget/python && python configure.py && ${MAKE}

livewidget-gui: src/livewidget/python/livewidget.so

livewidget-inplace: src/livewidget/python/livewidget.so
	-cp $(VOPT) src/livewidget/python/livewidget.so lib/nicos/clients/gui

livewidget-install:

livewidget-install-gui: src/livewidget/python/livewidget.so
	cp $(VOPT) src/livewidget/python/livewidget.so $(ROOTDIR)/lib/nicos/clients/gui

livewidget-clean:
	cd src/livewidget && ${MAKE} clean

T = test

test:
	@NOSE=`which nosetests`; if [ -z "$$NOSE" ]; then echo "nose is required to run the test suite"; exit 1; fi
	@$(PYTHON) `which nosetests` $(T) -e test_stresstest -d $(O)

testall:
	@NOSE=`which nosetests`; if [ -z "$$NOSE" ]; then echo "nose is required to run the test suite"; exit 1; fi
	@$(PYTHON) `which nosetests` $(T) -d $(O)

test-coverage:
	@NOSE=`which nosetests`; if [ -z "$$NOSE" ]; then echo "nose is required to run the test suite"; exit 0; fi
	@COVERAGE_PROCESS_START=.coveragerc $(PYTHON) `which nosetests` $(T) -d --with-coverage --cover-package=nicos $(O); \
	RESULT=$$?; \
	`which coverage || which python-coverage` combine; \
	`which coverage || which python-coverage` html -d cover; \
	echo "nosetest: $$RESULT"; \
	exit $$RESULT

lint:
	-PYTHONPATH=lib pylint --rcfile=./pylintrc lib/nicos/ $(shell find custom/ -name \*.py)

jenkinslintall: CUSTOMPYFILES = $(shell find custom/ -name \*.py)
jenkinslintall:
	-pylint --rcfile=./pylintrc --files-output=y lib/nicos/
	-if [[ -n "$(CUSTOMPYFILES)" ]]; then \
		pylint --rcfile=./pylintrc --files-output=y $(CUSTOMPYFILES); \
	else echo 'no custom python files'; fi


jenkinslint:
	-PYFILESCHANGED=$$(git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//' |grep "\.py"); \
	if [[ -n "$$PYFILESCHANGED" ]] ; then \
		pylint --rcfile=./pylintrc --files-output=y $$PYFILESCHANGED; \
	else echo 'no python files changed'; fi

changelint:
	PYFILESCHANGED=$$(git diff --name-status `git merge-base HEAD HEAD^` | sed -e '/^D/d' | sed -e 's/.\t//'  | grep "\.py"); \
	if [[ -n "$$PYFILESCHANGED" ]]; then \
		pylint --rcfile=./pylintrc $$PYFILESCHANGED; \
	else echo 'no python files changed'; fi

check:
	pyflakes lib/nicos custom/*/lib

# get the instrument from the full hostname (mira1.mira.frm2 -> mira)
INSTRUMENT = $(shell hostname -f | cut -d. -f2)
ifneq "$(INSTRUMENT)" ""
  INSTRDIR = $(wildcard custom/$(INSTRUMENT))
endif

# check for install customizations
ifeq "$(INSTRDIR)" ""
  INSTALL_ERR = $(error No customization found for instrument $(INSTRUMENT). \
    If this is not the correct instrument, use '${MAKE} install INSTRUMENT=instname', \
    where instname can also be "demo")
  # dummy targets
  custom-all:
  custom-inplace:
  custom-install:
  custom-clean:
  custom-gui:
else
  include $(INSTRDIR)/make.conf
  # check that the include provided all necessary variables
  ifeq "$(ROOTDIR)" ""
    INSTALL_ERR = $(error make.conf or cmdline must provide a value for ROOTDIR)
#  else ifeq "$(XXX)" ""
#    INSTALL_ERR = $(error make.conf or cmdline must provide a value for XXX)
  endif
endif

PYPLATFORM = $(shell $(PYTHON) -c 'import distutils.util as u; print u.get_platform()')
PYVERSION  = $(shell $(PYTHON) -c 'import sys; print sys.version[0:3]')

ifeq "$(V)" "1"
  VOPT = -v
else
  QOPT = -q
endif

install: all main-install custom-install

clean-upgrade:
	@echo "============================================================"
	@if [[ -e "$(ROOTDIR)/bin.bak" ]]; then \
		tools/mkbackup "${ROOTDIR)/bin.bak";fi
	@if [[ -e "$(ROOTDIR)/lib.bak" ]]; then \
		tools/mkbackup "${ROOTDIR)/lib.bak";fi
	@echo "Backing up old dirs....."
	@mv "$(ROOTDIR)/bin" "$(ROOTDIR)/bin.bak"
	@mv "$(ROOTDIR)/lib" "$(ROOTDIR)/lib.bak"
	@echo "Done ...."
	@echo "============================================================"

show-diff:
	@echo "Changes after upgrade"
	diff -ur $(ROOTDIR)/bin.bak $(ROOTDIR)/bin
	diff -ur $(ROOTDIR)/lib.bak $(ROOTDIR)/lib


upgrade: clean-upgrade install

main-install:
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing NICOS to $(ROOTDIR)..."
	@echo "============================================================="
	install $(VOPT) -d $(ROOTDIR)/{bin,doc,etc,lib,log,pid,setups,scripts}
	# the next line can be removed once all installations use the new scheme
	rm -f $(VOPT) $(ROOTDIR)/lib/nicos/services/daemon/_pyctl.so
	# install the C module in a platform-specific directory
	mkdir -p $(VOPT) $(ROOTDIR)/lib/plat-$(PYPLATFORM)
	mv $(VOPT) build/lib.$(PYPLATFORM)-$(PYVERSION)/nicos/services/daemon/_pyctl.so $(ROOTDIR)/lib/plat-$(PYPLATFORM)
	cp -pr $(VOPT) build/lib.$(PYPLATFORM)-$(PYVERSION)/* $(ROOTDIR)/lib
	cp -pr $(VOPT) pid/README $(ROOTDIR)/pid
	chown $(SYSUSER):$(SYSGROUP) $(ROOTDIR)/pid
	cp -pr $(VOPT) log/README $(ROOTDIR)/log
	chown $(SYSUSER):$(SYSGROUP) $(ROOTDIR)/log
	cp -pr $(VOPT) etc/nicos-system $(ROOTDIR)/etc
	cp -pr $(VOPT) build/scripts-$(PYVERSION)/* $(ROOTDIR)/bin
	-cp -pr $(VOPT) doc/build/html/* $(ROOTDIR)/doc
	$(PYTHON) etc/create_nicosconf.py "$(SYSUSER)" "$(SYSGROUP)" "$(NETHOST)" \
	  "$(ROOTDIR)/setups" "$(SERVICES)" "$(ENVIRONMENT)" > $(ROOTDIR)/nicos.conf
	if [ -f $(INSTRDIR)/gui/defconfig.py ]; then \
	  cp -p $(INSTRDIR)/gui/defconfig.py "$(ROOTDIR)/lib/nicos/clients/gui"; fi
	@echo "============================================================="
	@echo "Installing instrument specific modules..."
	@for custdir in custom/*; do \
		if [ -d $${custdir}/lib ]; then \
			mkdir -p $(VOPT) $(ROOTDIR)/lib/nicos/$${custdir#*/}; \
			cp -pr $(VOPT) $${custdir}/lib/* $(ROOTDIR)/lib/nicos/$${custdir#*/}; \
		fi; \
	done
	@echo "============================================================="
	@if [ "$(FRM2)" = 1 ]; then \
		echo "============================================================="; \
		echo "Installing FRM II specific modules..."; \
		mkdir -p $(VOPT) $(ROOTDIR)/lib/nicos/frm2; \
		cp -pr $(VOPT) custom/frm2/lib/* $(ROOTDIR)/lib/nicos/frm2; \
		echo "============================================================="; \
	fi
	@echo "Installing setups (backing up existing files)..."
	tools/copysetup $(INSTRDIR)/setups/ $(ROOTDIR)/setups
	@if [ "$(FRM2)" = 1 ]; then \
		echo "============================================================="; \
		echo "Installing FRM II specific setups (overwriting existing files!)..."; \
		mkdir $(VOPT) $(ROOTDIR)/setups/frm2; \
		cp -pr $(VOPT) custom/frm2/setups/* $(ROOTDIR)/setups/frm2; \
	fi
	@echo "============================================================="
	@echo "Running setup check..."
	-PYTHONPATH=$(ROOTDIR)/lib tools/check_setups $(ROOTDIR)/setups
	@echo "============================================================="
	@echo "Everything is now installed to $(ROOTDIR)."
	@echo "============================================================="
	@echo "Trying to create system-wide symbolic links..."
	-ln -sf $(VOPT) -t /etc/init.d $(ROOTDIR)/etc/nicos-system
	-ln -sf $(VOPT) -t /usr/bin $(ROOTDIR)/bin/*
	@echo "============================================================="
	@echo "Finished."
	@echo "============================================================="

install-gui: gui main-install-gui custom-install-gui

main-install-gui:
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing only NICOS GUI to $(ROOTDIR)..."
	@echo "============================================================="
	install $(VOPT) -d $(ROOTDIR)/{bin,lib,scripts}
	cp -pr $(VOPT) build/lib*/* $(ROOTDIR)/lib
	cp -pr $(VOPT) build/scripts*/nicos-gui $(ROOTDIR)/bin
	if [ -f $(INSTRDIR)/gui/defconfig.py ]; then \
	  cp -p $(INSTRDIR)/gui/defconfig.py "$(ROOTDIR)/lib/nicos/clients/gui"; fi
	@echo "============================================================="
	@echo "Installing custom modules..."
	mkdir -p $(VOPT) $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	cp -pr $(VOPT) $(INSTRDIR)/lib/* $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	@echo "============================================================="
	@echo "The GUI is now installed to $(ROOTDIR)."
	@echo "Trying to create system-wide symbolic link..."
	@echo "============================================================="
	-ln -sf $(VOPT) -t /usr/bin $(ROOTDIR)/bin/nicos-gui
	@echo "============================================================="
	@echo "Finished, now running custom install..."
	@echo "============================================================="

release:
	${MAKE} test
	cd doc; rm -r build/html; ${MAKE} html
	python setup.py sdist

fixsmb:
	chmod +x bin/*
	chmod +x etc/create_nicosconf.py
	chmod +x etc/nicos-system
	chmod +x custom/panda/bin/pausebutton
	chmod +x tools/check_setups
	chmod +x tools/mkbackup

help:
	@echo "Important targets:"
	@echo "  all           - build everything for installation except GUI"
	@echo "  inplace       - build everything for running NICOS from here"
	@echo "  gui           - build GUI"
	@echo
	@echo "  install       - install everything except GUI"
	@echo "  install-gui   - install GUI"
	@echo "  upgrade       - upgrade an existing install cleanly,"
	@echo "                   old files get backed up"
	@echo "    Customization autoselected for install: $(INSTRUMENT)"
	@echo "    Use '${MAKE} INSTRUMENT=instname ...' to select a different one;"
	@echo "    instname can also be test"
	@echo
	@echo "Development targets:"
	@echo "  test          - run test suite"
	@echo "  test-coverage - run test suite with coverage reporting"
	@echo "  check         - check source with pyflakes"
	@echo "  lint          - check source with pylint"
	@echo "  changelint    - check source with pylint(only files in last commit)"
	@echo "  release       - create tarball for official release"
