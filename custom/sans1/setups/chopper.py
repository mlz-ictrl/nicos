description = 'setup for the astrium chopper'

group = 'optional'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/chopper'

devices = dict(
    chopper_dru_rpm = device('devices.tango.WindowTimeoutAO',
        description = 'Chopper speed control',
        tangodevice = '%s/masterspeed' % tango_base,
        abslimits = (0, 20000),
        unit = 'rpm',
        fmtstr = '%.0f',
        timeout = 600,
        precision = 0.01,
        comdelay = 30,
        maxage = 35,
    ),
    chopper_watertemp = device('devices.tango.AnalogInput',
        description = 'Chopper water temp',
        tangodevice = '%s/watertemp' % tango_base,
        unit = 'l/min',
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
    ),
    chopper_waterflow = device('devices.tango.AnalogInput',
        description = 'Chopper water flow',
        tangodevice = '%s/flowrate' % tango_base,
        unit = 'l/min',
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
    ),
    chopper_vacuum = device('devices.tango.AnalogInput',
        description = 'Chopper vacuum pressure',
        tangodevice = '%s/vacuum' % tango_base,
        unit = 'mbar',
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
    ),
)

for i in xrange(1, 3):
    devices['chopper_ch%i_gear' % i] = device('devices.tango.AnalogOutput',
        description = 'Chopper channel %i gear' % i,
        tangodevice = '%s/ch%igear' % (tango_base, i),
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
    )
    devices['chopper_ch%i_phase' % i] = device('devices.tango.AnalogOutput',
        description = 'Chopper channel %i phase' % i,
        tangodevice = '%s/ch%iphase' % (tango_base, i),
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
    )
    devices['chopper_ch%i_speed' % i] = device('devices.tango.AnalogOutput',
        description = 'Chopper channel %i speed' % i,
        tangodevice = '%s/ch%ispeed' % (tango_base, i),
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
    )
