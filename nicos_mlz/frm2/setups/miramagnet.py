description = 'MIRA 0.5 T electromagnet'
group = 'plugplay'

includes = ['alias_B']

tango_base = 'tango://%s:10000/box/' % setupname

devices = dict(
    I_miramagnet = device('nicos.devices.entangle.RampActuator',
        description = 'MIRA Helmholtz magnet current',
        tangodevice = tango_base + 'plc/_i',
        abslimits = (-250, 250),
        fmtstr = '%.1f',
        unit = 'A',
    ),
    B_miramagnet = device('nicos.devices.generic.CalibratedMagnet',
        currentsource = 'I_miramagnet',
        description = 'MIRA magnetic field',
        # no abslimits: they are automatically determined from I
        unit = 'T',
        fmtstr = '%.4f',
    ),
    miramagnet_pol = device('nicos.devices.entangle.DigitalInput',
        description = 'Polarity of magnet current',
        tangodevice = tango_base + 'plc/_polarity',
        fmtstr = '%+d',
    ),
)

for i in range(1, 5):
    dev = device('nicos.devices.entangle.AnalogInput',
        description = 'Temperature %d of the miramagnet coils' % i,
        tangodevice = tango_base + 'plc/_t%d' % i,
        fmtstr = '%d',
        warnlimits = (0, 60),
        unit = 'degC',
    )
    devices['%s_T%d' % (setupname, i)] = dev

alias_config = {
    # I is included for the rare case you would need to use the current directly
    'B': {'B_miramagnet': 100, 'I_miramagnet': 80},
}

extended = dict(
    representative = 'B_miramagnet',
)
