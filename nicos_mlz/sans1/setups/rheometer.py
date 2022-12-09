description = 'Rheoplus worksheet remote control'

group = 'optional'

tango_base = 'tango://hw.sans1.frm2.tum.de:10000/rheo/'

devices = dict(
    Rheo_WS = device('nicos.devices.entangle.DigitalOutput',
        description = 'Worksheet to process',
        tangodevice = tango_base + 'rheo/worksheet',
        unit = '',
        fmtstr = 'No.%d',
    ),
)
