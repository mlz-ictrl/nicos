description = 'Reading Keithley multimeter as a counter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    busdaq = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'daq970/io',
        loglevel = 'info',
        visibility = (),
    ),

    busb2910 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'b2910bl/io',
        loglevel = 'info',
        visibility = (),
    ),
    #busk7001 = device('nicos.devices.entangle.StringIO',
    #    tangodevice = tango_base + 'k7001/io',
    #    loglevel = 'info',
    #    visibility = (),
    #),

    Current = device('nicos_mgml.devices.keysight_smu.Current',
        description = 'SMU Multimeter',
        fmtstr = '%.8f',
        b2910bl = 'busb2910',
        daq970 = 'busdaq',
    ),

    CurrentVolt = device('nicos.devices.generic.ParamDevice',
        description = 'voltage applied during current measurement',
        device = 'Current',
        parameter = 'voltage',
    ),
)
