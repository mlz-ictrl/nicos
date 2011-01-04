.PHONY: qrc so clean

PREFIX = 
RCC = $(PREFIX)pyrcc4

qrc:
	$(RCC) -o nicm/gui/gui_rc.py resources/nicm-gui.qrc

so:
	rm -rf build
	python setup.py build_ext
	cp build/lib*/nicm/daemon/*.so nicm/daemon

clean:
	find -name '*.pyc' -exec rm {} +
