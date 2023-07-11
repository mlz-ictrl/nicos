description = 'FUG HV power supply box'
group = 'plugplay'

tango_base = f'tango://{setupname}:10000/box/'

devices = {
    f'U_{setupname}': device('nicos.devices.entangle.PowerSupply',
        description = 'High voltage applied to sample',
        tangodevice = tango_base + 'fug/supply',
        fmtstr = '%.1f',
        unit = 'V',
        timeout = 60.0,
        precision = 0.1,
    ),
    f'{setupname}_current': device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'HV current',
        device = f'U_{setupname}',
        parameter = 'current',
    ),
}
