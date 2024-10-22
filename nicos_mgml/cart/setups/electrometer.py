description = 'Reading Keithley electrometer'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    busk6517 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k6517b/io',
        loglevel = 'info',
        visibility = (),
    ),

    Electrometer = device('nicos_mgml.devices.electrometer.K6517',
        description = 'Keithley 6517B electrometer',
        fmtstr = '%.8f',
        k6517 = 'busk6517',
        unit = 'pA'
    ),
)
