description = 'CAEN ELS FAST powersupplies'

group = 'lowlevel'

tango_base = 'tango://kompasshw.kompass.frm2.tum.de:10000/kompass/'

devices = dict(
    caenels1 = device('nicos.devices.entangle.PowerSupply',
        description = 'FAST power supply 1',
        tangodevice = tango_base + 'fastps1/ps',
        fmtstr = '%.4f',
        precision = 0.0001,
    ),
    caenels2 = device('nicos.devices.entangle.PowerSupply',
        description = 'FAST power supply 2',
        tangodevice = tango_base + 'fastps2/ps',
        fmtstr = '%.4f',
        precision = 0.0001,
    ),
)
