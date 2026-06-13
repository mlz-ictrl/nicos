description = 'quench detection logger'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    quench_signal = device('nicos.devices.entangle.DigitalInput',
        description = 'current signal of quench detection',
        tangodevice = tango_base + 'datalogger/plc_analog1',
    ),

    quench_events = device('nicos.devices.entangle.DigitalInput',
        description = 'number of logged events on datalogger PLC',
        tangodevice = tango_base + 'datalogger/plc_numevents',
    ),

    quench_last = device('nicos_mlz.j_nse.devices.datalogger.LastEvent',
        description = 'time of last event',
        tangodevice = tango_base + 'datalogger/plc_lastevent',
    ),
)
