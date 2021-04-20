description = 'postion of Monitor: X in beam; Z may be motor'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']

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
    hv_mon1 = device('nicos.devices.entangle.PowerSupply',
        description = 'HV monitor 1',
        tangodevice = tango_base + 'monitor1/hv/voltage',
        requires = {'level': 'admin'},
        lowlevel = True,
    ),
    hv_mon2 = device('nicos.devices.entangle.PowerSupply',
        description = 'HV monitor 2',
        tangodevice = tango_base + 'monitor2/hv/voltage',
        requires = {'level': 'admin'},
        lowlevel = True,
    ),
    hv_mon3 = device('nicos.devices.entangle.PowerSupply',
        description = 'HV monitor 2',
        tangodevice = tango_base + 'monitor3/hv/voltage',
        requires = {'level': 'admin'},
        lowlevel = True,
    ),
    hv_mon4 = device('nicos.devices.entangle.PowerSupply',
        description = 'HV monitor 4',
        tangodevice = tango_base + 'monitor4/hv/voltage',
        requires = {'level': 'admin'},
        lowlevel = True,
    ),
    hv_mon = device('nicos_mlz.refsans.devices.devicealias.HighlevelDeviceAlias'),
)

alias_config = {
    'hv_mon':  {
        'hv_mon1': 100,
        'hv_mon2': 100,
        'hv_mon3': 100,
        'hv_mon4': 100,
    },
}
