description = 'Secondary slit devices'

group = 'optional'

devices = dict(
    sst = device('nicos.devices.generic.Axis',
        description = 'SST',
        motor = device('nicos.devices.entangle.Motor',
            fmtstr = '%.2f',
            tangodevice = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/channel6/motor',
        ),
        precision = 0.01,
    ),
    ssw = device('nicos.devices.generic.Axis',
        description = 'Secondary Slit Width',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = 'tango://stressictrl.stressi.frm2:10000/stressi/schunk/motor',
            fmtstr = '%.1f',
            # unit = 'mm',
            # abslimits = (0, 60),
            # userlimits = (0, 20),
            # requires =  {'level': 'admin'},
        ),
        precision = 0.01,
    ),
)
