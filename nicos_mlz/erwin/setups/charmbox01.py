description = 'Montoring devices for the CHARM detector'

group = 'lowlevel'

tango_base = 'tango://erwinhw.erwin.frm2.tum.de:10000/erwin/charmbox01/cb'

devices = dict(
    charm1_flow = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'flow',
        visibility = (),
    ),
    charm1_pdet = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'p1',
        visibility = ()
    ),
    charm1_ppump1 = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'p2',
        visibility = ()
    ),
)

for i in range(1, 4):
    devices[f'charm1_t{i}'] = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + f't{i}',
        visibility = ()
    )
