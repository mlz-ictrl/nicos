description = '3He detector'
group = 'lowlevel'

includes = ['filesavers']

tango_base = 'tango://%s:10000/reseda/' % configdata('gconfigs.tango_host')

devices = dict(
    timer = device('nicos.devices.generic.VirtualTimer',
    # timer = device('nicos.devices.entangle.TimerChannel',
        description = 'Timer channel 2',
    #    tangodevice = tango_base + 'frmctr/timer',
        fmtstr = '%.2f',
        # visibility = (),
        unit = 's',
    ),
    # monitor1 = device('nicos.devices.entangle.CounterChannel',
    #     description = 'Monitor channel 1',
    #     tangodevice = tango_base + 'frmctr/counter0',
    #     type = 'monitor',
    #     fmtstr = '%d',
    #     # visibility = (),
    #     unit = 'cts'
    # ),
    # monitor2 = device('nicos.devices.entangle.CounterChannel',
    #     description = 'Monitor channel 2',
    #     tangodevice = tango_base + 'frmctr/counter1',
    #     type = 'monitor',
    #     fmtstr = '%d',
    #     visibility = (),
    # ),
    # mon_hv = device('nicos.devices.entangle.PowerSupply',
    #     description = 'High voltage power supply of the monitor',
    #     tangodevice = tango_base + 'mon/hv',
    #     abslimits = (0, 1050),
    #     unit = 'V',
    # ),
    # counter = device('nicos.devices.entangle.CounterChannel',
    #     description = 'Counter channel 1',
    #     tangodevice = tango_base + 'frmctr/counter2',
    #     type = 'counter',
    #     fmtstr = '%d',
    #     # visibility = (),
    #     unit = 'cts',
    # ),
)
