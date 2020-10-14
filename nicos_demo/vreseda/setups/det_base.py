#  -*- coding: utf-8 -*-

description = '3He detector'

group = 'optional'

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
        description = 'Timer channel 2',
        fmtstr = '%.2f',
        unit = 's',
    ),
    monitor1 = device('nicos.devices.generic.VirtualCounter',
        description = 'Monitor channel 1',
        type = 'monitor',
        fmtstr = '%d',
        unit = 'cts'
    ),
    # monitor2 = device('nicos.devices.generic.VirtualCounter',
    # description = 'Monitor channel 2',
    # tangodevice = '%s/frmctr/counter1' % tango_base,
    # type = 'monitor',
    # fmtstr = '%d',
    # lowlevel = True,
    # ),
    # mon_hv = device('nicos.devices.tango.PowerSupply',
    #     description = 'High voltage power supply of the monitor',
    #     tangodevice = '%s/mon/hv' % tango_base,
    #     abslimits = (0, 1050),
    #     unit = 'V',
    # ),
    counter = device('nicos.devices.generic.VirtualCounter',
        description = 'Counter channel 1',
        type = 'counter',
        fmtstr = '%d',
        unit = 'cts',
    ),
)
