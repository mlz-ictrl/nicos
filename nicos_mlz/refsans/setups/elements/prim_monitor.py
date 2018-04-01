description = 'postion of Monitor: X in beam; Z may be motor'

group = 'optional'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost


devices = dict(
    prim_monitor_z = device('nicos.devices.generic.ManualSwitch',
        description = 'how is the z pos',
        states = ['const x from b3'],
        fmtstr = '%s',
        unit = 'foo',
    ),
    # prim_monitor_z = device('nicos.devices.taco.Motor',
    #     description = 'Monitor axis motor',
    #     tacodevice = '%s/phytron/kanal_09' % tacodev, !bg2
    #     abslimits = (10, 300),
    # ),
    prim_monitor_x = device('nicos.devices.generic.ManualMove',
        description = 'pos of monitor in beam',
        abslimits = (0, 500),
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    prim_monitor_typ = device('nicos.devices.generic.ManualSwitch',
        description = 'which monitor is in use?',
        states = ['#1','#2','#3'],
        fmtstr = 'Typ %d',
        unit = '',
    ),
)
