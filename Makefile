.PHONY: all install clean inplace test

RCC = pyrcc4

all: lib/nicos/gui/gui_rc.py
	python setup.py build

lib/nicos/gui/gui_rc.py: resources/nicos-gui.qrc
	$(RCC) -o lib/nicos/gui/gui_rc.py resources/nicos-gui.qrc

clean:
	rm -rf build
	find -name '*.pyc' -exec rm -f {} +

inplace:
	rm -rf build
	python setup.py build_ext
	cp build/lib*/nicos/daemon/*.so lib/nicos/daemon

test:
	@python test/run.py

# get the instrument from the full hostname (mira1.mira.frm2 -> mira)
INSTRUMENT = $(shell hostname -f | cut -d. -f2)
INSTRDIR = $(wildcard custom/$(INSTRUMENT))

# check for install customizations
ifeq "$(INSTRDIR)" ""
  INSTALL_ERR = $(error No customization found for instrument $(INSTRUMENT), \
                        use 'make install INSTRUMENT=instname')
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

install: all
	$(INSTALL_ERR)
	@echo "============================================================="
	@echo "Installing NICOS-ng to $(ROOTDIR)..."
	@echo "============================================================="
	install $(VOPT) -d $(ROOTDIR)/{bin,doc,etc,lib,log,pid,setups,scripts}
	cp -pr $(VOPT) build/lib*/* $(ROOTDIR)/lib
	cp -pr $(VOPT) pid/README $(ROOTDIR)/pid
	cp -pr $(VOPT) log/README $(ROOTDIR)/log
	cp -pr $(VOPT) etc/nicos-system $(ROOTDIR)/etc
	cp -pr $(VOPT) build/scripts*/* $(ROOTDIR)/bin
	cp -pr $(VOPT) doc/build/html/* $(ROOTDIR)/doc
	cp -pr $(VOPT) $(INSTRDIR)/setups/* $(ROOTDIR)/setups
	python etc/create_nicosconf.py "$(SYSUSER)" "$(SYSGROUP)" "$(NETHOST)" > $(ROOTDIR)/nicos.conf
	@echo "============================================================="
	@echo "Everything is now installed to $(ROOTDIR)."
	@echo "Trying to create system-wide symbolic links..."
	@echo "============================================================="
	-ln -s $(VOPT) -t /etc/init.d $(ROOTDIR)/etc/nicos-system
	-ln -s $(VOPT) -t /usr/bin $(ROOTDIR)/bin/*
	@echo "============================================================="
	@echo "Finished."
	@echo "============================================================="
