description = 'Vacuum sensors of sample chamber'

group = 'lowlevel'

tango_base = 'tango://pgaahw.pgaa.frm2:10000/pgaa/sample/'

devices = dict(
    chamber_pressure = device('nicos.devices.entangle.Sensor',
        description = 'vacuum sensor in sample chamber',
        tangodevice = tango_base + 'vacuum',
        fmtstr = '%.2g',
        pollinterval = 15,
        maxage = 60,
        warnlimits = (None, 1),
    ),
)
