description = 'Additional rotation table'

group = 'optional'

tango_base = 'tango://motorbox05.stressi.frm2.tum.de:10000/box/'

devices = dict(
    addphi_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel4/motor',
        fmtstr = '%.2f',
        lowlevel = True,
        speed = 4,
    ),
    addphi = device('nicos.devices.generic.Axis',
        description = 'Additional rotation table',
        motor = 'addphi_m',
        precision = 0.01,
    ),
)
