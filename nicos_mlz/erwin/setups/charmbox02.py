description = 'Montoring devices for the CHARM detector'

group = 'lowlevel'

tango_base = 'tango://erwinhw.erwin.frm2.tum.de:10000/erwin/charmbox02/'

devices = dict(
    charm2_flow = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'flow',
        visibility = (),
    ),
)

for i in range(1, 4):
    devices[f'charm2_t{i}'] = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + f't{i}',
        visibility = ()
    )
    devices[f'charm2_p{i}'] = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + f'p{i}',
        visibility = ()
    )
