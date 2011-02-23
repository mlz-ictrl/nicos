.PHONY: all install clean inplace test

RCC = pyrcc4

all: nicos/gui/gui_rc.py
	python setup.py build

nicos/gui/gui_rc.py: resources/nicos-gui.qrc
	$(RCC) -o nicos/gui/gui_rc.py resources/nicos-gui.qrc

clean:
	rm -rf build
	find -name '*.pyc' -exec rm -f {} +

inplace:
	rm -rf build
	python setup.py build_ext
	cp build/lib*/nicos/daemon/*.so nicos/daemon

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

install: all
# display error and exit if one was found
	$(INSTALL_ERR)
# create all directories
	install -d $(ROOTDIR)/pid $(ROOTDIR)/log $(ROOTDIR)/scripts \
	    $(ROOTDIR)/lib $(ROOTDIR)/bin $(ROOTDIR)/doc $(ROOTDIR)/setups
# copy Python packages, scripts, docs, setups
	cp -prv build/lib*/* $(ROOTDIR)/lib
	cp -prv build/scripts*/* $(ROOTDIR)/bin
	cp -prv doc/build/html/* $(ROOTDIR)/doc
	cp -prv $(INSTRDIR)/setups/* $(ROOTDIR)/setups
	python etc/create_nicosconf.py $(ROOTDIR) \
	       "$(SYSUSER)" "$(SYSGROUP)" "$(NETHOST)" > $(ROOTDIR)/nicos.conf
# copy init script
	-install -m a+x etc/nicos-system /etc/init.d
# finished
	@echo
	@echo "All set."