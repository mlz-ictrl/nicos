description = 'Heinzinger power supplies for MIEZE'

group = 'optional'

tango_base = 'tango://heinzinger.mira.frm2:10000/box/'

devices = dict(
    hrf1 = device('nicos.devices.tango.PowerSupply',
        description = 'first Heinzinger',
        tangodevice = tango_base + 'heinzinger1/curr',
        unit = 'A',
    ),
    hrf2 = device('nicos.devices.tango.PowerSupply',
        description = 'second Heinzinger',
        tangodevice = tango_base + 'heinzinger2/curr',
        unit = 'A',
    ),
)
