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
    ),
    chopper_ch2_phase = device('nicos.devices.tango.AnalogOutput',
        description = 'Chopper channel 2 phase',
        tangodevice = '%s/ch2phase' % tango_base,
        fmtstr = '%.2f',
        comdelay = 30,
        maxage = 35,
    )
)
