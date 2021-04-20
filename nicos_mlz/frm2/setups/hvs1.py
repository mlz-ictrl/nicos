description = 'FUG HV power supply box'
group = 'plugplay'

tango_base = 'tango://%s:10000/box/' % setupname

devices = {
    'U_%s' % setupname: device('nicos.devices.entangle.PowerSupply',
        description = 'High voltage applied to sample',
        tangodevice = tango_base + 'fug/supply',
        fmtstr = '%.1f',
        unit = 'V',
        timeout = 60.0,
        precision = 0.1,
    ),
    '%s_current' % setupname: device('nicos.devices.generic.ReadonlyParamDevice',
        description = 'HV current',
        device = 'U_%s' % setupname,
        parameter = 'current',
    ),
}
