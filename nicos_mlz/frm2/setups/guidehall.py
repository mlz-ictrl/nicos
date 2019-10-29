description = 'FRM II Neutron guide hall west infrastructure devices'

group = 'lowlevel'

tango_base = 'tango://ictrlfs.ictrl.frm2:10000/'

devices = dict(
    Sixfold = device('nicos.devices.tango.NamedDigitalInput',
        description = 'Sixfold shutter status',
        mapping = {'closed': 0,
                   'open': 1},
        pollinterval = 60,
        maxage = 120,
        tangodevice = tango_base + 'mlz/shutter/sixfold',
    ),
    Crane = device('nicos.devices.tango.AnalogInput',
        description = 'The position of the crane in the guide '
        'hall West measured from the east end',
        tangodevice = tango_base + 'frm2/smc10/pos',
        pollinterval = 5,
        maxage = 30,
        unit = 'm',
        fmtstr = '%.1f',
    ),
)
