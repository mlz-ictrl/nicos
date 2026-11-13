description = 'LaDiff monochromator'

group = 'lowlevel'

tango_base = 'tango://hw.ladiff.frm2.tum.de:10000/beckhoff/mono/'

devices = dict(
    m_att = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Attenuator at monochromator',
        tangodevice = tango_base + '_attenuator',
        mapping = {
            'out':  0,
            'Att1': 1,
            'Att2': 2,
            'Att1+Att2': 3,
        },
    ),
    shutter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Instrument shutter',
        tangodevice = tango_base + '_attenuator',
        mapping = {
            'open': 1,
            'closed': 0,
        },
    ),
)

for dev in ('mth', 'mtt', 'mtx', 'mty', 'mfh', 'mfv', 'mgx'):
    devices[dev] = device('nicos.devices.generic.Axis',
        description = f'{dev} axis',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + f'_{dev}_mot',
        ),
        coder = device('nicos.devices.entangle.Sensor',
            tangodevice = tango_base + f'_{dev}_enc',
        ),
        precision = 0.001,
    )

for i in range(1, 22):
    devices[f'msb{i}'] = device('nicos.devices.entangle.NamedDigitalInput',
                                description = f'Mobile block {i}',
                                tangodevice = tango_base + f'_msb{i}',
                                mapping = dict(up = 1, down = 0),
                                unit = '',
                                )

