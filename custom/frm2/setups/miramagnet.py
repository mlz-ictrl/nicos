description = 'MIRA 0.5 T electromagnet'
group = 'plugplay'

includes = ['alias_B']

tango_url = 'tango://%s:10000/box/beckhoff' % setupname

devices = dict(
    I_miramagnet   = device('devices.tango.Actuator',
                            description = 'MIRA Helmholtz magnet current',
                            tangodevice = '%s/plc_i' % tango_url,
                            abslimits = (-250, 250),
                            fmtstr = '%.1f',
                           ),
    B_miramagnet   = device('devices.generic.CalibratedMagnet',
                            currentsource = 'I',
                            description = 'MIRA magnetic field',
                            # no abslimits: they are automatically determined from I
                            unit = 'T',
                            fmtstr = '%.4f',
                           ),
    miramagnet_pol = device('devices.tango.DigitalInput',
                            description = 'Polarity of magnet current',
                            tangodevice = '%s/plc_polarity' % tango_url,
                            fmtstr = '%+d',
                           ),
)

for i in range(1, 5):
    dev = device('devices.tango.AnalogInput',
                 description = 'Temperature %d of the miramagnet coils' % i,
                 tangodevice = '%s/plc_t%d' % (tango_url, i),
                 fmtstr = '%d',
                 warnlimits = (0, 60),
                 unit = 'degC',
                )
    devices['%s_T%d' % (setupname, i)] = dev

alias_config = {
    # I is included for the rare case you would need to use the current directly
    'B': {'B_miramagnet': 100, 'I_miramagnet': 80},
}
