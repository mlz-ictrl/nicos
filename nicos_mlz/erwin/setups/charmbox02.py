description = 'Montoring devices for the CHARM detector'

group = 'lowlevel'

tango_base = 'tango://erwinhw.erwin.frm2.tum.de:10000/erwin/charmbox02/_'

devices = dict(
    charm2_flow = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'flow',
        visibility = (),
    ),
    charm2_pdet = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'p1',
        visibility = ()
    ),
    charm2_ppump1 = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'p2',
        visibility = ()
    ),
    charm2_ppump2 = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'p3',
        visibility = ()
    ),
)

for i in range(1, 4):
    devices[f'charm2_t{i}'] = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + f't{i}',
        visibility = ()
    )
