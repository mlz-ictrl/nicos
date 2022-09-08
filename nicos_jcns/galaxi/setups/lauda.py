description = 'GALAXI Lauda temperature controller setup'
group = 'optional'

tango_base = 'tango://phys.galaxi.jcns.fz-juelich.de:10000/galaxi/'
lauda = tango_base + 'lauda/'

devices = dict(
    T = device('nicos.devices.generic.DeviceAlias'),
    Ts = device('nicos.devices.generic.DeviceAlias'),
    T_lauda_intern = device('nicos.devices.entangle.TemperatureController',
        description = 'Lauda regulated to internal (bath) sensor.',
        tangodevice = lauda + 'controller_int',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        window = 10,
    ),
    T_lauda_extern = device('nicos.devices.entangle.TemperatureController',
        description = 'Lauda regulated to external sensor.',
        tangodevice = lauda + 'controller_ext',
        unit = 'degC',
        fmtstr = '%.2f',
        precision = 0.1,
        window = 10,
    ),
)

alias_config = {
    'T':  {'T_lauda_intern': 100, 'T_lauda_extern': 110},
    'Ts': {'T_lauda_intern': 100, 'T_lauda_extern': 110},
}

startupcode = '''
AddEnvironment(T, Ts)
'''
