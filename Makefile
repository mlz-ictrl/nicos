.PHONY: all install clean inplace test main-install

RCC = pyrcc4
PYTHON = /usr/bin/python

all: lib/nicos/gui/gui_rc.py
	$(PYTHON) setup.py build -e "/usr/bin/env python"
	$(PYTHON) etc/set_version.py build/lib*
	-make custom-all

lib/nicos/gui/gui_rc.py: resources/nicos-gui.qrc
	$(RCC) -o lib/nicos/gui/gui_rc.py resources/nicos-gui.qrc

clean:
	rm -rf build
	find -name '*.pyc' -exec rm -f {} +
	-make custom-clean

inplace:
	rm -rf build
	$(PYTHON) setup.py build_ext
	cp build/lib*/nicos/daemon/*.so lib/nicos/daemon
	-make custom-inplace

test:
	@$(PYTHON) test/run.py $(O)

lint:
	-pylint --rcfile=./pylintrc lib/nicos/

jenkinslintall:
	-pylint --rcfile=./pylintrc --files-output=y lib/nicos/

jenkinslint:
	-pylint --rcfile=./pylintrc  --files-output=y  `git diff --name-only HEAD HEAD^ | grep ".py"`

changelint:
	-pylint --rcfile=./pylintrc  `git diff --name-only HEAD | grep ".py"`

check:
	pyflakes lib/nicos custom/*/lib

test-coverage:
	@$(PYTHON) test/run.py --with-coverage --cover-package=nicos --cover-html $(O)

# get the instrument from the full hostname (mira1.mira.frm2 -> mira)
INSTRUMENT = $(shell hostname -f | cut -d. -f2)
ifneq "$(INSTRUMENT)" ""
  INSTRDIR = $(wildcard custom/$(INSTRUMENT))
endif

# check for install customizations
ifeq "$(INSTRDIR)" ""
  INSTALL_ERR = $(error No customization found for instrument $(INSTRUMENT). \
    If this is not the correct instrument, use 'make install INSTRUMENT=instname', \
    where instname can also be "test")
  # dummy targets
  custom-all:
  custom-inplace:
  custom-install:
  custom-clean:
else
  include $(INSTRDIR)/make.conf
  # check that the include provided all necessary variables
  ifeq "$(ROOTDIR)" ""
    INSTALL_ERR = $(error make.conf or cmdline must provide a value for ROOTDIR)
#  else ifeq "$(XXX)" ""
#    INSTALL_ERR = $(error make.conf or cmdline must provide a value for XXX)
  endif
endif

ifeq "$(V)" "1"
  VOPT = -v
endif

install: all main-install custom-install

main-install:
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing NICOS to $(ROOTDIR)..."
	@echo "============================================================="
	install $(VOPT) -d $(ROOTDIR)/{bin,doc,etc,lib,log,pid,setups,scripts}
	rm -f $(VOPT) $(ROOTDIR)/lib/nicos/daemon/_pyctl.so
	cp -pr $(VOPT) build/lib*/* $(ROOTDIR)/lib
	cp -pr $(VOPT) pid/README $(ROOTDIR)/pid
	chown $(SYSUSER):$(SYSGROUP) $(ROOTDIR)/pid
	cp -pr $(VOPT) log/README $(ROOTDIR)/log
	chown $(SYSUSER):$(SYSGROUP) $(ROOTDIR)/log
	cp -pr $(VOPT) etc/nicos-system $(ROOTDIR)/etc
	cp -pr $(VOPT) build/scripts*/* $(ROOTDIR)/bin
	-cp -pr $(VOPT) doc/build/html/* $(ROOTDIR)/doc
	$(PYTHON) etc/create_nicosconf.py "$(SYSUSER)" "$(SYSGROUP)" "$(NETHOST)" \
	  "$(ROOTDIR)/setups" "$(SERVICES)" > $(ROOTDIR)/nicos.conf
	if [ -f $(INSTRDIR)/gui/defconfig.py ]; then \
	  cp -p $(INSTRDIR)/gui/defconfig.py "$(ROOTDIR)/lib/nicos/gui"; fi
	@echo "============================================================="
	@echo "Installing custom modules..."
	mkdir -p $(VOPT) $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	cp -pr $(VOPT) $(INSTRDIR)/lib/* $(ROOTDIR)/lib/nicos/$(INSTRUMENT)
	@echo "============================================================="
	@echo "Installing setups (not overwriting existing files)..."
	cp -prn $(VOPT) $(INSTRDIR)/setups/* $(ROOTDIR)/setups
	@echo "============================================================="
	@echo "Everything is now installed to $(ROOTDIR)."
	@echo "Trying to create system-wide symbolic links..."
	@echo "============================================================="
	-ln -sf $(VOPT) -t /etc/init.d $(ROOTDIR)/etc/nicos-system
	-ln -sf $(VOPT) -t /usr/bin $(ROOTDIR)/bin/*
	@echo "============================================================="
	@echo "Finished."
	@echo "============================================================="

release:
	make test
	cd doc; rm -r build/html; make html
	python setup.py sdist
