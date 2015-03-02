all: corbadevice_idl.py absdev_idl.py

corbadevice_idl.py:	corbadevice.idl
	omniidl -bpython -Wbfactories -Wbstubs=nicos.devices.vendor.caress corbadevice.idl
	mv nicos/devices/vendor/caress/corbadevice_idl.py .
	sed -i '1,1i#pylint: skip-file' corbadevice_idl.py
	rm -rf nicos

absdev_idl.py:	absdev.idl
	omniidl -bpython -Wbfactories -Wbstubs=nicos.devices.vendor.caress absdev.idl
	mv nicos/devices/vendor/caress/absdev_idl.py .
	sed -i '1,1i#pylint: skip-file' absdev_idl.py
	rm -rf nicos

clean:
	rm -rf nicos CARESS CARESS__POA corbadevice_idl.py absdev_idl.py
