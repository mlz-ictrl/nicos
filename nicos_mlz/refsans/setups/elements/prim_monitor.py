description = 'postion of Monitor: X in beam; Z may be motor'

group = 'lowlevel'

devices = dict(
    prim_monitor_z = device('nicos.devices.generic.ManualMove',
        description = 'Monitor axis motor',
        abslimits = (-10, 300),
        default = 0,
        unit = 'mm',
    ),
    prim_monitor_x = device('nicos.devices.generic.ManualMove',
        description = 'pos of monitor in beam',
        abslimits = (0, 500),
        default = 0,
        fmtstr = '%.1f',
        unit = 'mm',
    ),
    prim_monitor_typ = device('nicos.devices.generic.ManualSwitch',
        description = 'which monitor is in use?',
        states = ['None', '#1', '#2', '#3', '#4', '#5', '#6', '#7'],
        fmtstr = 'Typ %d',
        unit = '',
    ),
)
