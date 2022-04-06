description = 'Devices to read out the nano digital multimeter'

group = 'optional'

tango_base = 'tango://puma5.puma.frm2.tum.de:10000/puma/nanodmm/'

devices = dict(
    vout = device('nicos.devices.entangle.Sensor',
        description = 'Digital nano volt meter for electrical field',
        tangodevice = tango_base + 'voltage',
    ),
)
