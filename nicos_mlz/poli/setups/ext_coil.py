description = 'external coil for preparing sample state'

group = 'optional'

tango_base = 'tango://phys.poli.frm2:10000/poli/'

devices = dict(
    samplecoil = device('nicos.devices.tango.PowerSupply',
        description = 'Sample guide field',
        tangodevice = tango_base + 'samplecoil/supply',
        fmtstr = '%.2f',
        unit = 'A',
        pollinterval = 10,
        maxage = 25,
    ),
)
