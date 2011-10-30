.PHONY: all install clean inplace test main-install

RCC = pyrcc4
PYTHON = /usr/bin/python

all: lib/nicos/gui/gui_rc.py cascade
	$(PYTHON) setup.py build -e "/usr/bin/env python"
	$(PYTHON) etc/set_version.py build/lib*

lib/nicos/gui/gui_rc.py: resources/nicos-gui.qrc
	$(RCC) -o lib/nicos/gui/gui_rc.py resources/nicos-gui.qrc

clean:
	rm -rf build
	find -name '*.pyc' -exec rm -f {} +
	cd src/cascade && make clean

inplace: cascade
	rm -rf build
	$(PYTHON) setup.py build_ext
	cp build/lib*/nicos/daemon/*.so lib/nicos/daemon
	-cp src/cascade/nicosclient/pythonbinding/cascadeclient.so lib/nicos/mira
	-cp src/cascade/nicoswidget/pythonbinding/cascadewidget.so lib/nicos/gui

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


test-coverage:
	@$(PYTHON) test/run.py --with-coverage --cover-package=nicos --cover-html

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

install: all cascade-install main-install custom-install

main-install:
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing NICOS-ng to $(ROOTDIR)..."
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

ifeq "$(NEEDSCASCADE)" "1"
cascade:
	cd src/cascade && make nicosmodules
cascade-install:
	cp $(VOPT) src/cascade/nicosclient/pythonbinding/cascadeclient.so $(ROOTDIR)/lib/nicos/mira
	-cp $(VOPT) src/cascade/nicoswidget/pythonbinding/cascadewidget.so $(ROOTDIR)/lib/nicos/gui
else
cascade:
cascade-install:
endif
