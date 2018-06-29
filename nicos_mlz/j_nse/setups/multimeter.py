description = 'multimeter channels'

group = 'optional'

tango_base = 'tango://phys.j-nse.frm2:10000/j-nse/'

devices = dict(
    coil_res = device('nicos.devices.tango.VectorInput',
        description = 'vacuum in coil 2 vessel',
        tangodevice = tango_base + 'dmm/ch',
        unit = 'Ohm',
        fmtstr = '%.3g',
        pollinterval = 10,
        maxage = 25,
    ),

    datalog_events = device('nicos.devices.tango.DigitalInput',
        description = 'number of logged events on datalogger PLC',
        tangodevice = tango_base + 'datalogger/plc_numevents',
    ),

    datalog_last = device('nicos_mlz.j_nse.devices.datalogger.LastEvent',
        description = 'time of last event',
        tangodevice = tango_base + 'datalogger/plc_lastevent',
    ),
)
