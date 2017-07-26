all: corbadevice_idl.py

corbadevice_idl.py:	corbadevice.idl
	omniidl -bpython -Wbfactories -Wbstubs=nicos.delab corbadevice.idl
	mv nicos/delab/corbadevice_idl.py .
	sed -i '1,1i#pylint: skip-file' corbadevice_idl.py
	rm -rf nicos

clean:
	rm -rf nicos CARESS CARESS__POA corbadevice_idl.py
