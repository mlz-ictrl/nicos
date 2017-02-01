description = 'Rheoplus worksheet remote control'

group = 'optional'

tango_base = 'tango://phys.kws2.frm2:10000/rheo/'

devices = dict(
    Rheo_WS = device('devices.tango.DigitalOutput',
                     description = 'Worksheet to process',
                     tangodevice = tango_base + 'rheo/worksheet',
                     fmtstr = 'No. %d',
                     unit = '',
                    ),
)
