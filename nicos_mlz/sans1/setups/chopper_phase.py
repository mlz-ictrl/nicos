description = 'setup for the astrium chopper phase'

group = 'optional'

excludes = ['chopper']

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/chopper'

devices = dict(
    chopper_ch1_phase = device('nicos.devices.tango.AnalogOutput',
        description = 'Chopper channel 1 phase',
        tangodevice = '%s/ch1phase' % tango_base,
        fmtstr = '%.2f',
        comdelay = 30,
        maxage = 35,
        warnlimits = (16.18, 16.22),
    ),
    chopper_ch2_phase = device('nicos.devices.tango.AnalogOutput',
        description = 'Chopper channel 2 phase',
        tangodevice = '%s/ch2phase' % tango_base,
        fmtstr = '%.2f',
        comdelay = 30,
        maxage = 35,
        warnlimits = (4.78, 4.82),
    ),
    chopper_ch1_parkingpos = device('nicos.devices.tango.AnalogOutput',
        description = 'Chopper channel 1 parking position',
        tangodevice = '%s/ch1parkingpos' % tango_base,
        fmtstr = '%.2f',
        comdelay = 30,
        maxage = 35,
        warnlimits = (16.18, 16.22),
    ),
    chopper_ch2_parkingpos = device('nicos.devices.tango.AnalogOutput',
        description = 'Chopper channel 2 parking position',
        tangodevice = '%s/ch2parkingpos' % tango_base,
        fmtstr = '%.2f',
        comdelay = 30,
        maxage = 35,
        warnlimits = (4.78, 4.82),
    ),
    chopper_waterflow = device('nicos.devices.tango.AnalogInput',
        description = 'Chopper water flow',
        tangodevice = '%s/flowrate' % tango_base,
        unit = 'l/min',
        fmtstr = '%.3f',
        comdelay = 30,
        maxage = 35,
        warnlimits = (1.5, 100),
    ),
)
