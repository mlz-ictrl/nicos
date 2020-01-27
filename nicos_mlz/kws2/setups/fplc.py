description = 'Connection to FPLC spectrometer'

group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    fplc_trigger = device('nicos_mlz.kws2.devices.fplc.FPLCTrigger',
        description = 'Triggers FPLC measurement',
        input = device('nicos.devices.tango.DigitalInput',
            tangodevice = tango_base + 'fplc/plc_finished',
            lowlevel = True,
        ),
        output = device('nicos.devices.tango.DigitalOutput',
            tangodevice = tango_base + 'fplc/plc_trigger',
            lowlevel = True,
        ),
    ),
    fplc_rate = device('nicos_mlz.kws2.devices.fplc.FPLCRate',
        description = 'Forwards detector countrate to FPLC',
        tangodevice = tango_base + 'fplc/countrate',
        pollinterval = 1,
        rate = 'det_img',
    ),
)

extended = dict(
    poller_cache_reader = ['det_img'],
)
