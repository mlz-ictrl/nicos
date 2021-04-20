description = 'Aircontrol PLC devices'

group = 'optional'

tango_base = 'tango://kompasshw.kompass.frm2:10000/kompass/aircontrol/plc_'

devices = dict(
    spare_motor_x2 = device('nicos.devices.entangle.Motor',
        description = 'spare motor',
        tangodevice = tango_base + 'spare_mot_x2',
        fmtstr = '%.4f',
        lowlevel = True,
    ),
    shutter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'neutron shutter',
        tangodevice = tango_base + 'shutter',
        mapping = dict(closed=0, open=1),
    ),
    key = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'supervisor mode key',
        tangodevice = tango_base + 'key',
        mapping = dict(normal=0, super_visor_mode=1),
        requires = dict(level='admin'),
    ),
)

for key in ('analyser', 'detector', 'sampletable'):
    devices['airpad_' + key] = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'switches the airpads at %s' % key,
        tangodevice = tango_base + 'airpads_%s' % key,
        mapping = dict(on=1, off=0),
    )
    devices['p_%s' % key] = device('nicos.devices.entangle.Sensor',
        description = 'supply pressure for %s airpads',
        tangodevice = tango_base + 'p_%s' % key,
        unit = 'bar',
        lowlevel = True,
    )


for key in ('ana', 'arm', 'det', 'st'):
    for idx in (1, 2, 3):
        devices['p_airpad_%s_%d' % (key, idx)] = device('nicos.devices.entangle.Sensor',
            description = 'actual pressure in airpad %d of %s' % (idx, key),
            tangodevice = tango_base + 'p_airpad_%s_%d' % (key, idx),
            unit = 'bar',
            lowlevel = True,
        )

for key in (1, 2, 3, 4):
    devices['aircontrol_t%d' % key] = device('nicos.devices.entangle.Sensor',
        description = 'aux temperatures sensor %d' % key,
        tangodevice = tango_base + 'temperature_%d' % key,
        unit = 'degC',
    )


#for key in range(1, 52+1):
#    devices['msb%d' % key] = device('nicos.devices.entangle.NamedDigitalOutput',
#        description = 'mono shielding block %d' % key,
#        tangodevice = tango_base + 'plc_msb%d' % key,
#        mapping = dict(up=1, down=0),
#    )
