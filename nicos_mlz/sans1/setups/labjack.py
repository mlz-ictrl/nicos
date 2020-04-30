description = 'labjack ai0 and ai1'

group = 'optional'

tango_base = 'tango://sans1hw.sans1.frm2:10000/sans1/'

devices = dict(
    ai0 = device('nicos.devices.tango.Sensor',
        description = 'Analog Input 0',
        tangodevice = tango_base + 'labjack/ai0',
        fmtstr = '%.5f',
        pollinterval = 0.5,
        maxage = 2,
        lowlevel = False,
    ),
    ai1 = device('nicos.devices.tango.Sensor',
        description = 'Analog Input 1',
        tangodevice = tango_base + 'labjack/ai1',
        fmtstr = '%.5f',
        pollinterval = 0.5,
        maxage = 2,
        lowlevel = False,
    ),
)
